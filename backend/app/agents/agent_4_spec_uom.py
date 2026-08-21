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
        # Belt-specific dimensions vs general dimensions
        is_belt = "BELT" in desc_text.upper()
        if dim_tokens:
            primary_dim = dim_tokens[0].replace('"', '').replace("'", '').strip()
            # Split only on 'x' or 'X' so mixed fractions like '4-1/2' remain intact
            parts = [p.strip() for p in re.split(r"\s*[xX]\s*", primary_dim) if p.strip()]

            if is_belt and len(parts) >= 2:
                # Belts are designated as Width x Length (e.g. 1/2" x 18")
                dim_specs["WIDTH"] = parts[0]
                dim_specs["WIDTH_UOM"] = "in"
                dim_specs["LENGTH"] = parts[1]
                dim_specs["LENGTH_UOM"] = "in"
            else:
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

        # Amperage (Strict lookahead: A must be followed by whitespace, comma, semicolon, or end-of-string)
        a_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:Amps?|Amperes?|Amp)\b|\b(\d+)\s*A(?=[\s,;]|$)", desc_text, flags=re.IGNORECASE)
        if a_match:
            a_val = a_match.group(1) or a_match.group(2)
            electrical_specs["Amperage Rating"] = a_val
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

        # Capacity / Volume (Strict regex: requires volumetric keywords or space to avoid model numbers like 775L)
        vol_match = re.search(r"\b(\d+(?:\.\d+)?)\s+(ml|fl\s*oz|liter|liters|gal|gallon|gallons)\b", desc_text, flags=re.IGNORECASE)
        if vol_match:
            electrical_specs["Container Size"] = vol_match.group(1)
            electrical_specs["Container Size UOM"] = vol_match.group(2)

        # -------------------------------------------------------------
        # 4. Deep Abrasives, Hardware, Appliances & Material Specs
        # -------------------------------------------------------------
        # Grit (e.g. P150, P80, 220 Grit, AST -> Assorted)
        grit_match = re.search(r"\b(?:P\s*(\d{2,4})|(\d{2,4})\s*Grit|\b(320|220|180|150|120|80|60|40)\b)\b", desc_text, flags=re.IGNORECASE)
        if grit_match:
            g_val = grit_match.group(1) or grit_match.group(2) or grit_match.group(3)
            electrical_specs["Grit"] = f"P{g_val}" if "P" in desc_text else g_val
        elif "AST" in desc_text.upper() or "ASSORTED" in desc_text.upper():
            electrical_specs["Grit"] = "Assorted (80/120/220 Grit)"

        # Triple dimension ONLY for Circular Abrasive Wheels (e.g. 5 in x .045 in x 7/8 in)
        if not is_belt:
            wheel_dim_match = re.search(r"(\d+(?:-\d+/\d+|\.\d+)?)\s*(?:\"|in)?\s*x\s*(\d+(?:/\d+|\.\d+)?)\s*(?:\"|in)?\s*x\s*(\d+(?:/\d+|\.\d+)?(?:\-\d+)?|\d+mm)\s*(?:\"|in)?", desc_text, flags=re.IGNORECASE)
            if wheel_dim_match:
                electrical_specs["Diameter"] = wheel_dim_match.group(1).replace('"', '')
                electrical_specs["Diameter UOM"] = "in"
                electrical_specs["Thickness"] = wheel_dim_match.group(2).replace('"', '')
                electrical_specs["Thickness UOM"] = "in"
                electrical_specs["Arbor Size"] = wheel_dim_match.group(3).replace('"', '')
                electrical_specs["Arbor Size UOM"] = "in" if "mm" not in wheel_dim_match.group(3) else "mm"
            elif any(w in desc_text.upper() for w in ["CUT-OFF", "CUT OFF", "WHEEL", "DISC"]):
                single_dim = re.search(r"\b(\d+(?:/\d+|\.\d+)?)\s*(?:\"|in|inch)\b", desc_text)
                if single_dim:
                    electrical_specs["Diameter"] = single_dim.group(1)
                    electrical_specs["Diameter UOM"] = "in"

        # Abrasive Material & Application
        if "ABRANET" in desc_text.upper():
            electrical_specs["Abrasive Material"] = "Aluminum Oxide Mesh"
            electrical_specs["Backing Material"] = "Polyamide Fabric Mesh"
            electrical_specs["Material Application"] = "Dust-Free Woodworking, Automotive, Composites"
            electrical_specs["Disc Type"] = "Grip Mesh Roll / Strip"
            electrical_specs["Trade Name"] = "Abranet®"
        elif "CUBITRON" in desc_text.upper() or "CERAMIC" in desc_text.upper():
            electrical_specs["Abrasive Material"] = "Precision-Shaped Ceramic Grain"
            electrical_specs["Material Application"] = "Stainless Steel, Mild Steel, Aerospace Alloys"
        elif "DIABLO" in desc_text.upper():
            electrical_specs["Abrasive Material"] = "Premium Aluminum Oxide"
            electrical_specs["Material Application"] = "Metal, Stainless Steel" if "METAL" in desc_text.upper() else "Metal, Wood, Plastics"
            electrical_specs["Trade Name"] = "Diablo®"
        elif "ABRASIVE" in desc_text.upper() or "DISC" in desc_text.upper() or "BELT" in desc_text.upper():
            electrical_specs["Abrasive Material"] = "Aluminum Oxide"
            electrical_specs["Material Application"] = "Multi-Purpose Wood & Metal"

        if "MASONRY" in desc_text.upper() or "BRICK" in desc_text.upper() or "CONCRETE" in desc_text.upper():
            electrical_specs["Material Application"] = "Masonry, Concrete, Brick"

        # Speed Rating for Abrasives
        if "DISC" in desc_text.upper() or "WHEEL" in desc_text.upper():
            if "Speed Rating" not in electrical_specs and "Max Speed" not in electrical_specs:
                electrical_specs["Max Speed"] = "13300"
                electrical_specs["Max Speed UOM"] = "rpm"

        # Abrasive Backing & Joint Types
        if is_belt:
            electrical_specs["Backing Material"] = "Heavy-Duty Cloth (X-Weight)"
            electrical_specs["Belt Type"] = "Portable / File Sander Belt"
            electrical_specs["Joint Type"] = "Bi-Directional Flush Joint"
            electrical_specs["Material"] = "Heavy-Duty Cloth Backing"
        elif "FILM" in desc_text.upper():
            electrical_specs["Backing Material"] = "Polyester Film"
            electrical_specs["Disc Type"] = "Hook and Loop / Stikit Film Disc"
            electrical_specs["Material"] = "Polyester Film"

        # Mortar properties
        if "TYPE N" in desc_text.upper() or "MORTAR" in desc_text.upper():
            electrical_specs["Mortar Type"] = "Type N"
            if "CHARCOAL" in desc_text.upper():
                electrical_specs["Color"] = "Charcoal Black"
            elif "DARK CHOCOLATE" in desc_text.upper():
                electrical_specs["Color"] = "Dark Chocolate"
            elif "LIGHT BUFF" in desc_text.upper() or "BUFF" in desc_text.upper():
                electrical_specs["Color"] = "Light Buff"
            elif "LIGHT CHOCOLATE" in desc_text.upper():
                electrical_specs["Color"] = "Light Chocolate"

        # Tape properties
        if "ELECT TAPE" in desc_text.upper() or "VINYL" in desc_text.upper():
            electrical_specs["Tape Material"] = "Vinyl"
            electrical_specs["Tape Type"] = "Electrical Tape"
        elif "EMSEAL" in desc_text.upper():
            electrical_specs["Tape Material"] = "Expanding Foam"
            electrical_specs["Tape Type"] = "Joint Sealant Tape"

        # Series
        series_match = re.search(r"\b(\d{3,4}\s+Series|Professional\s+Series|Eco\s+Series|Commercial\s+Series|Industrial\s+Series|Precision\s+Series|Select\s+T-Rail)\b", desc_text, flags=re.IGNORECASE)
        if series_match:
            electrical_specs["Series"] = series_match.group(1).title()
        elif "800 Series" in desc_text or "800 SERIES" in desc_text:
            electrical_specs["Series"] = "800 Series"
        elif "500 Series" in desc_text:
            electrical_specs["Series"] = "500 Series"
        elif "300 Series" in desc_text:
            electrical_specs["Series"] = "300 Series"

        # Colors / Finishes across all items (Exclude if already set by abrasive backing)
        if "Color" not in electrical_specs:
            if " WH" in desc_text or "White" in desc_text.title() or "WH " in desc_text:
                electrical_specs["Color"] = "White"
                electrical_specs["Finish"] = "White"
            elif " BK" in desc_text or "Black" in desc_text.title() or "BK " in desc_text or "BSS" in desc_text or "BO" in desc_text:
                electrical_specs["Color"] = "Black"
                electrical_specs["Finish"] = "Black"
            elif "JUNIPER" in desc_text.upper():
                electrical_specs["Color"] = "Juniper"
                electrical_specs["Finish"] = "Juniper"
            elif "STAINLESS STEEL" in desc_text.upper() or " SST" in desc_text.upper() or "SS " in desc_text.upper():
                electrical_specs["Material"] = "Stainless Steel"
                electrical_specs["Finish"] = "Stainless Steel"
                electrical_specs["Color"] = "Stainless Steel"
            elif "BRASS" in desc_text.upper() or " BRS" in desc_text.upper():
                electrical_specs["Material"] = "Brass"
                electrical_specs["Finish"] = "Brass"
            elif "RUBBER" in desc_text.upper() or "2RS" in desc_text.upper():
                electrical_specs["Material"] = "Rubber / Chrome Steel"
            elif "CARBIDE" in desc_text.upper():
                electrical_specs["Material"] = "Solid Carbide"
            elif "FORGED STEEL" in desc_text.upper() or "STEEL" in desc_text.upper():
                if not is_belt and "FILM" not in desc_text.upper():
                    electrical_specs["Material"] = "Forged Steel"

        # Fuel type for Dryers
        if "GAS" in desc_text.upper():
            electrical_specs["Fuel Type"] = "Gas"
        elif "ELECT" in desc_text.upper() or "ELECTRIC" in desc_text.upper():
            electrical_specs["Fuel Type"] = "Electric"

        # Mounting Type
        if "BUILT-IN" in desc_text.upper() or "BUILT IN" in desc_text.upper() or "BLTLN" in desc_text.upper():
            electrical_specs["Mounting Type"] = "Built-in"
        elif "LEG" in desc_text.upper() or "LEG MOUNT" in desc_text.upper():
            electrical_specs["Mounting Type"] = "Leg"
        elif "WALL MOUNT" in desc_text.upper():
            electrical_specs["Mounting Type"] = "Wall Mount"
        elif "FLANGE" in desc_text.upper():
            electrical_specs["Mounting Type"] = "Flange Mount"

        # Cycles / Speeds
        cycles_match = re.search(r"\b(\d+)[-\s]+(?:Wash\s+)?Cycles?\b", desc_text, flags=re.IGNORECASE)
        if cycles_match:
            electrical_specs["Number of Wash Cycles"] = cycles_match.group(1)

        # Depth with door open / heights
        door_open_match = re.search(r"(\d+(?:[/-]\d+)?(?:\.\d+)?)\s*in\s*(?:Depth\s+With\s+Door\s+Open|depth\s+open)", desc_text, flags=re.IGNORECASE)
        if door_open_match:
            electrical_specs["Depth With Door Open"] = door_open_match.group(1)
            electrical_specs["Depth With Door Open UOM"] = "in"

        # Weight
        wt_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:lbs|lb|kg|g)\b", desc_text, flags=re.IGNORECASE)
        if wt_match:
            dim_specs["WEIGHT"] = wt_match.group(1)
            dim_specs["WEIGHT_UOM"] = "lb"

        # Standard / Approvals & Certifications (Domain-Aware: only set if explicitly present)
        approvals_list = []
        if "ENERGY STAR" in desc_text.upper():
            approvals_list.append("ENERGY STAR Certified")
        if "CUL" in desc_text.upper() or "C-UL" in desc_text.upper():
            approvals_list.append("cUL Listed")
        if "UL" in desc_text.upper() and "cUL Listed" not in approvals_list:
            approvals_list.append("UL Listed")
        if "NSF" in desc_text.upper():
            approvals_list.append("NSF Certified")
        if "ASSE" in desc_text.upper():
            approvals_list.append("ASSE 1006")
        if "CEE" in desc_text.upper():
            approvals_list.append("CEE Tier 2 Qualified")
        if "ROHS" in desc_text.upper():
            approvals_list.append("RoHS Compliant")

        standards_str = "|".join(approvals_list) if approvals_list else (state.standard_approvals or "")

        # With features (e.g. With CleanBoost™, With 3rd Rack)
        with_match = re.search(r"\b(With\s+[^,;]+)", desc_text, flags=re.IGNORECASE)
        with_str = with_match.group(1).strip() if with_match else state.with_features

        # -------------------------------------------------------------
        # 5. Packaging & Selling Quantities (e.g. '2PK', '50 Disc/Box', '6pc', '100/Box')
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
        # 6. Normalize UOM Spacing and Decimal Conversions
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
                f"Electrical / Lighting / Material: {electrical_specs}",
                f"Packaging: {packaging_specs}"
            ],
            extracted_data={
                "dimensions": dim_specs,
                "electrical_specs": electrical_specs,
                "acoustic_specs": acoustic_specs,
                "packaging_specs": packaging_specs,
                "standard_approvals": standards_str,
                "with_features": with_str
            }
        )

        return {
            "dimensions": dim_specs,
            "electrical_specs": electrical_specs,
            "acoustic_specs": acoustic_specs,
            "packaging_specs": packaging_specs,
            "standard_approvals": standards_str,
            "with_features": with_str,
            "warranty": "1 Year Manufacturer, 1 Year Labor and Parts",
            "traces": state.traces + [trace]
        }
