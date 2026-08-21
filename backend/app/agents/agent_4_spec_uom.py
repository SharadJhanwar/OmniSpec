import time
import re
from typing import Dict, Any, List, Optional
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..services.uom_converter import UOMConverter
from ..services.decimal_fraction import DecimalFractionEngine
from ..core.logging import logger


class SpecUOMExtractorAgent:
    """
    Agent 4: Deterministic Spec, Dimension, Electrical & Lighting UOM Extraction Agent
    Extracts physical dimensions, electrical ratings, acoustic levels, lighting specs, and industrial packaging.
    Enforces Master UOM standards (space separation) and exact 63 Decimal-to-Fraction conversions.
    """

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        desc_text = state.cleaned_part_desc or ""
        token_bag = state.token_bag or {}
        dim_tokens = token_bag.get("dimensions", [])
        pack_raw = token_bag.get("pack_qty", "")

        dim_specs: Dict[str, str] = {}
        electrical_specs: Dict[str, str] = {}
        acoustic_specs: Dict[str, str] = {}
        packaging_specs: Dict[str, str] = {}

        # -------------------------------------------------------------
        # 1. Dimension Parsing (Triplets, Lumber notation 1nx6-16', etc.)
        # -------------------------------------------------------------
        # Check for lumber/decking pattern (e.g. 1nx6-16' or 1x12-12' or 1x6 16ft)
        lumber_match = re.search(r"(\d+)(?:nx|x)(\d+)[-\s]+(\d+)'?", desc_text, flags=re.IGNORECASE)
        if lumber_match:
            dim_specs["HEIGHT"] = lumber_match.group(1)
            dim_specs["HEIGHT_UOM"] = "in"
            dim_specs["WIDTH"] = lumber_match.group(2)
            dim_specs["WIDTH_UOM"] = "in"
            dim_specs["LENGTH"] = lumber_match.group(3)
            dim_specs["LENGTH_UOM"] = "ft"
        elif dim_tokens:
            primary_dim = dim_tokens[0].replace('"', '').replace("'", '').strip()
            # Split only on 'x' or 'X' so mixed fractions like '4-1/2' remain intact
            parts = [p.strip() for p in re.split(r"\s*[xX]\s*", primary_dim) if p.strip()]

            if len(parts) >= 1:
                dim_specs["LENGTH"] = parts[0]
                dim_specs["LENGTH_UOM"] = "in"
            if len(parts) >= 2:
                dim_specs["WIDTH"] = parts[1]
                dim_specs["WIDTH_UOM"] = "in"
            if len(parts) >= 3:
                dim_specs["HEIGHT"] = parts[2]
                dim_specs["HEIGHT_UOM"] = "in"

        # Check for explicitly stated Dimensions in Dishwashers / Large items
        explicit_dim = re.search(r"(\d+(?:[/-]\d+)?(?:\.\d+)?)\s*in\s*W\s*x\s*(\d+(?:[/-]\d+)?(?:\.\d+)?)\s*in\s*D", desc_text, flags=re.IGNORECASE)
        if explicit_dim:
            dim_specs["WIDTH"] = explicit_dim.group(1)
            dim_specs["WIDTH_UOM"] = "in"
            dim_specs["LENGTH"] = explicit_dim.group(2)
            dim_specs["LENGTH_UOM"] = "in"

        # -------------------------------------------------------------
        # 2. Electrical & Lighting Specifications
        # -------------------------------------------------------------
        # Voltage
        v_match = re.search(r"\b(\d+)\s*(?:V|VAC|Volts)\b", desc_text, flags=re.IGNORECASE)
        if v_match:
            electrical_specs["Voltage Rating"] = v_match.group(1)
            electrical_specs["Voltage Rating UOM"] = "V"
        elif "120V" in desc_text or "120 V" in desc_text:
            electrical_specs["Voltage Rating"] = "120"
            electrical_specs["Voltage Rating UOM"] = "V"
        elif "20V" in desc_text or "20 V" in desc_text:
            electrical_specs["Voltage Rating"] = "20"
            electrical_specs["Voltage Rating UOM"] = "V"

        # Amperage
        a_match = re.search(r"\b(\d+)\s*(?:A|Amps|Amperes)\b", desc_text, flags=re.IGNORECASE)
        if a_match:
            electrical_specs["Amperage Rating"] = a_match.group(1)
            electrical_specs["Amperage Rating UOM"] = "A"
        elif "15A" in desc_text or "15 A" in desc_text:
            electrical_specs["Amperage Rating"] = "15"
            electrical_specs["Amperage Rating UOM"] = "A"

        # Wattage (e.g. 60W, 9.5W, 40W, 100W)
        w_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:W|Watts|Watt)\b", desc_text, flags=re.IGNORECASE)
        if w_match:
            electrical_specs["Wattage"] = w_match.group(1)
            electrical_specs["Wattage UOM"] = "W"

        # Color Temperature (e.g. 27K -> 2700 K, 30K -> 3000 K, 50K -> 5000 K)
        cct_match = re.search(r"\b(27|30|35|40|50|65)K\b", desc_text, flags=re.IGNORECASE)
        if cct_match:
            cct_val = f"{cct_match.group(1)}00"
            electrical_specs["Color Temperature"] = cct_val
            electrical_specs["Color Temperature UOM"] = "K"

        # Base Type (e.g. MED -> Medium E26, CANDLE -> Candelabra E12, GU10)
        if "MED" in desc_text.upper() or "E26" in desc_text.upper():
            electrical_specs["Base Type"] = "Medium E26"
        elif "CANDLE" in desc_text.upper() or "E12" in desc_text.upper():
            electrical_specs["Base Type"] = "Candelabra E12"
        elif "GU10" in desc_text.upper():
            electrical_specs["Base Type"] = "GU10"

        # Bulb Shape (e.g. A19, BR30, PAR38, T8, B11)
        shape_match = re.search(r"\b(A19|BR30|PAR38|PAR30|PAR20|T8|T5|B11|G25)\b", desc_text, flags=re.IGNORECASE)
        if shape_match:
            electrical_specs["Bulb Shape"] = shape_match.group(1).upper()

        # -------------------------------------------------------------
        # 3. Acoustic Ratings (e.g. 47 dBA, 41 dBA)
        # -------------------------------------------------------------
        dba_match = re.search(r"\b(\d+)\s*(?:dBA|dB|Decibels)\b", desc_text, flags=re.IGNORECASE)
        if dba_match:
            acoustic_specs["Sound Level"] = dba_match.group(1)
            acoustic_specs["Sound Level UOM"] = "dBA"

        # -------------------------------------------------------------
        # 3b. Generalized Industrial Ratings (Pressure, Speed, Flow, Gauge, Power)
        # -------------------------------------------------------------
        # Pressure (e.g. 3500 PSI, 60 PSI)
        psi_match = re.search(r"\b(\d+)\s*(?:PSI|psi|bar)\b", desc_text, flags=re.IGNORECASE)
        if psi_match:
            electrical_specs["Pressure Rating"] = psi_match.group(1)
            electrical_specs["Pressure Rating UOM"] = "PSI"

        # Speed (e.g. 13300 RPM, 2400 RPM)
        rpm_match = re.search(r"\b(\d+)\s*(?:RPM|rpm)\b", desc_text, flags=re.IGNORECASE)
        if rpm_match:
            electrical_specs["Speed Rating"] = rpm_match.group(1)
            electrical_specs["Speed Rating UOM"] = "rpm"

        # Flow Rate (e.g. 3000 GPM, 45 GPM)
        gpm_match = re.search(r"\b(\d+)\s*(?:GPM|gpm)\b", desc_text, flags=re.IGNORECASE)
        if gpm_match:
            electrical_specs["Flow Rate"] = gpm_match.group(1)
            electrical_specs["Flow Rate UOM"] = "GPM"

        # Horsepower (e.g. 1/3 HP, 1.5 HP, 2 HP)
        hp_match = re.search(r"\b(\d+(?:\.\d+)?|\d+/\d+)\s*(?:HP|hp|Horsepower)\b", desc_text, flags=re.IGNORECASE)
        if hp_match:
            electrical_specs["Power Rating"] = hp_match.group(1)
            electrical_specs["Power Rating UOM"] = "HP"

        # Interrupt Rating (e.g. 10 kAIC)
        kaic_match = re.search(r"\b(\d+)\s*(?:kAIC|kaic|kA)\b", desc_text, flags=re.IGNORECASE)
        if kaic_match:
            electrical_specs["Interrupt Rating"] = kaic_match.group(1)
            electrical_specs["Interrupt Rating UOM"] = "kAIC"

        # Wire Gauge (e.g. 10-18 AWG, 12 AWG)
        awg_match = re.search(r"\b(\d+(?:-\d+)?)\s*(?:AWG|awg)\b", desc_text, flags=re.IGNORECASE)
        if awg_match:
            electrical_specs["Wire Gauge"] = awg_match.group(1)
            electrical_specs["Wire Gauge UOM"] = "AWG"

        # Capacity / Volume (e.g. 10 ml, 50 ml, 16 oz)
        vol_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(ml|oz|fl oz|liter|L)\b", desc_text, flags=re.IGNORECASE)
        if vol_match:
            electrical_specs["Container Size"] = vol_match.group(1)
            electrical_specs["Container Size UOM"] = vol_match.group(2)

        # -------------------------------------------------------------
        # 4. Packaging & Selling Quantities (e.g. '2PK', '50 Disc/Box', '6pc', '100/Box')
        # -------------------------------------------------------------
        box_match = re.search(r"\b(\d+)\s*/\s*(?:Box|box|Pack|pack|Pk|pk)\b", desc_text, flags=re.IGNORECASE)
        pk_match = re.search(r"\b(\d+)\s*(?:PK|Pack|pc|piece|Disc/Box)\b", desc_text, flags=re.IGNORECASE)
        if box_match:
            q = box_match.group(1)
            packaging_specs["Selling Qty"] = q
            packaging_specs["Selling UOM"] = f"{q}/Box"
            packaging_specs["Standard Packaging Information"] = f"{q}/Box"
        elif pk_match:
            q = pk_match.group(1)
            packaging_specs["Selling Qty"] = q
            packaging_specs["Selling UOM"] = f"{q}/PK"
            packaging_specs["Standard Packaging Information"] = f"{q}/PK"
        elif pack_raw:
            qty_match = re.search(r"\b(\d+)\b", pack_raw)
            if qty_match:
                packaging_specs["Selling Qty"] = qty_match.group(1)
                packaging_specs["Selling UOM"] = "Box" if "box" in pack_raw.lower() else "Pack"
                packaging_specs["Standard Packaging Information"] = pack_raw
        else:
            packaging_specs["Selling Qty"] = "1"
            packaging_specs["Selling UOM"] = "Each"
            packaging_specs["Standard Packaging Information"] = "1 Each"

        # -------------------------------------------------------------
        # 5. Normalize UOM Spacing and Decimal Conversions
        # -------------------------------------------------------------
        for k, v in dim_specs.items():
            if not k.endswith("_UOM") and v:
                try:
                    # Check if decimal needs conversion to fraction
                    v_float = float(v)
                    if v_float != int(v_float) and v_float > 0.05:
                        dim_specs[k] = DecimalFractionEngine.decimal_to_fraction(v_float)
                except ValueError:
                    pass

        trace = AgentTrace(
            agent_name="Agent 4: Spec, Dimension & UOM Extractor",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Dimensions: {dim_specs}",
                f"Electrical / Lighting: {electrical_specs}",
                f"Packaging: {packaging_specs}"
            ],
            extracted_data={
                "dimensions": dim_specs,
                "electrical_specs": electrical_specs,
                "acoustic_specs": acoustic_specs,
                "packaging_specs": packaging_specs
            }
        )

        return {
            "dimensions": dim_specs,
            "electrical_specs": electrical_specs,
            "acoustic_specs": acoustic_specs,
            "packaging_specs": packaging_specs,
            "traces": state.traces + [trace]
        }
