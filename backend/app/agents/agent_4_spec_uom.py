import time
import re
from typing import Dict, Any, List, Optional
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..services.uom_converter import UOMConverter
from ..services.decimal_fraction import DecimalFractionEngine
from ..core.logging import logger


class SpecUOMExtractorAgent:
    """
    Agent 4: Deterministic Spec, Dimension & UOM Extraction Agent
    Extracts physical dimensions, electrical ratings, acoustic levels, and industrial packaging.
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

        # 1. Parse Dimension Triplet (e.g. 5"x.045"x7/8" or 4-1/2"x.045"x7/8" or 1x12-12')
        if dim_tokens:
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

        # 2. Parse Electrical Ratings (e.g., 120V, 15A, 240 kW-hr)
        v_match = re.search(r"\b(\d+)\s*(?:V|VAC|Volts)\b", desc_text, flags=re.IGNORECASE)
        if v_match:
            electrical_specs["Voltage Rating"] = v_match.group(1)
            electrical_specs["Voltage Rating UOM"] = "V"
        elif "120V" in desc_text or "120 V" in desc_text:
            electrical_specs["Voltage Rating"] = "120"
            electrical_specs["Voltage Rating UOM"] = "V"

        a_match = re.search(r"\b(\d+)\s*(?:A|Amps|Amperes)\b", desc_text, flags=re.IGNORECASE)
        if a_match:
            electrical_specs["Amperage Rating"] = a_match.group(1)
            electrical_specs["Amperage Rating UOM"] = "A"
        elif "15A" in desc_text or "15 A" in desc_text:
            electrical_specs["Amperage Rating"] = "15"
            electrical_specs["Amperage Rating UOM"] = "A"

        # 3. Parse Acoustic Ratings (e.g. 47 dBA, 41 dBA)
        dba_match = re.search(r"\b(\d+)\s*(?:dBA|dB|Decibels)\b", desc_text, flags=re.IGNORECASE)
        if dba_match:
            acoustic_specs["Sound Level"] = dba_match.group(1)
            acoustic_specs["Sound Level UOM"] = "dBA"

        # 4. Parse Packaging & Selling Quantities (e.g. '10pc', '50 Disc/Box', '6pc')
        if pack_raw:
            qty_match = re.search(r"\b(\d+)\b", pack_raw)
            if qty_match:
                packaging_specs["Selling Qty"] = qty_match.group(1)
                packaging_specs["Selling UOM"] = "Box" if "box" in pack_raw.lower() else "Pack"
        else:
            packaging_specs["Selling Qty"] = "1"
            packaging_specs["Selling UOM"] = "Each"

        # 5. Normalize UOM Spacing and Decimal Conversions
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
                f"Electrical: {electrical_specs}",
                f"Acoustic: {acoustic_specs}",
                f"Packaging: {packaging_specs}"
            ],
            extracted_data={
                "dimensions": dim_specs,
                "electrical": electrical_specs,
                "acoustic": acoustic_specs,
                "packaging": packaging_specs
            }
        )

        return {
            "dimensions": dim_specs,
            "electrical_specs": electrical_specs,
            "acoustic_specs": acoustic_specs,
            "packaging_specs": packaging_specs,
            "traces": state.traces + [trace]
        }
