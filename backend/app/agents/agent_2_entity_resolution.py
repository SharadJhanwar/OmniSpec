import time
import re
from typing import Dict, Any, Tuple
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..db.duckdb_client import kb
from ..core.logging import logger


class EntityResolutionAgent:
    """
    Agent 2: Brand & Entity Resolution Agent
    Resolves noisy supplier strings and description tokens to canonical UniCat 27K
    Manufacturers and Brands with legal casing and mandatory registered marks (®, ™).
    """

    # MPN Prefix -> Known Brand hints
    MPN_PREFIX_MAP = {
        "PDSH": "FRIGIDAIRE",
        "WDTS": "WHIRLPOOL",
        "DCB": "DIABLO",
        "DBD": "DIABLO",
        "DFB": "DIABLO",
        "3MABR": "3M",
        "9A-": "MIRKA",
        "5B-": "MIRKA",
        "49-94": "MILWAUKEE",
        "ADR": "AZEK",
        "ADCR": "AZEK"
    }

    # Extended distributor co-op list to identify non-OEM suppliers
    DISTRIBUTOR_MAP = {
        "APPDE": "Appliance Dealers Cooperative",
        "JAMIN": "Jam Industrial Supply LLC",
        "BOICA": "Boise Cascade Building Materials",
        "USLUMBER": "U S Lumber",
        "PARKSITE": "Parksite",
        "FASTENAL": "Fastenal Company"
    }

    # Brand line / Trade name mappings
    TRADE_NAME_PATTERNS = {
        "Cubitron": "Cubitron™ II",
        "Diablo": "Diablo®",
        "Steel Demon": "Steel Demon",
        "Speed Demon": "Speed Demon",
        "Performance+": "Performance+",
        "Perform+": "Performance+",
        "Ceramic+": "Ceramic+",
        "Stikit": "Stikit™",
        "Abranet": "Abranet®",
        "HIOLIT": "HIOLIT",
        "Enhance Naturals": "Enhance Naturals",
        "Enhance Basics": "Enhance Basics",
        "Select 2.0": "Select 2.0",
        "Lineage": "Lineage",
        "Vintage": "Vintage",
        "Landmark": "Landmark",
        "Harvest": "Harvest",
        "Professional": "Professional Series",
        "Eco": "Eco Series"
    }

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        desc_text = state.cleaned_part_desc or ""
        supp_name = state.clean_supplier_name or ""
        vendor_code = (state.supplier_vendor_code or "").upper()
        mpn = (state.clean_mfg_part_num or "").strip()

        mfr_name = ""
        brand_name = ""
        trade_name = ""
        conf = 0.0

        # Step 1: Detect Trade Name / Product Line
        for key, canonical_trade in cls.TRADE_NAME_PATTERNS.items():
            if re.search(rf"\b{re.escape(key)}\b", desc_text, flags=re.IGNORECASE):
                trade_name = canonical_trade
                break

        # Step 2: Check if supplier is a known distributor co-op
        is_distributor = vendor_code in cls.DISTRIBUTOR_MAP or any(
            d.lower() in supp_name.lower() for d in cls.DISTRIBUTOR_MAP.values()
        )

        brand_match = None

        # Step 3: Priority 1 - Explicit Clean Brand Candidates from Input (E1_Brand, DIB_Brand, etc.)
        brand_candidates = state.token_bag.get("brand_candidates", [])
        for cand in brand_candidates:
            if not cand:
                continue
            cand_u = cand.upper()
            # Skip if candidate is a distributor code or distributor company name
            if cand_u in cls.DISTRIBUTOR_MAP or any(d.upper() in cand_u for d in cls.DISTRIBUTOR_MAP.values()):
                continue
            brand_match = kb.find_brand(cand)
            if brand_match:
                break

        # Step 4: Priority 2 - Check MPN Prefix Map
        if not brand_match and mpn:
            for prefix, mapped_brand in cls.MPN_PREFIX_MAP.items():
                if mpn.upper().startswith(prefix):
                    brand_match = kb.find_brand(mapped_brand)
                    if brand_match:
                        break

        # Step 5: Priority 3 - Search Description Words for Known Brands
        if not brand_match and desc_text:
            desc_words = desc_text.split()
            for w in desc_words:
                clean_w = re.sub(r"[^A-Za-z0-9]", "", w)
                if len(clean_w) >= 2:
                    brand_match = kb.find_brand(clean_w)
                    if brand_match:
                        break

        # Step 6: Priority 4 - If supplier is NOT a distributor, match supplier name
        if not brand_match and not is_distributor and supp_name:
            brand_match = kb.find_brand(supp_name)

        # Step 7: Assign canonical results
        if brand_match:
            mfr_name, brand_name, conf = brand_match
        elif supp_name and not is_distributor:
            mfr_name = supp_name
            brand_name = supp_name
            conf = 0.70
        else:
            mfr_name = supp_name or "Unassigned Manufacturer"
            brand_name = supp_name or "Unbranded"
            conf = 0.40

        # Step 8: Alternate Part Number derivation
        alt_mpn = mpn.replace("-", "").replace(".", "").strip()
        if alt_mpn == mpn:
            alt_mpn = ""

        trace = AgentTrace(
            agent_name="Agent 2: Brand & Entity Resolution",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Resolved: '{brand_name}' ({mfr_name}) [Score: {conf*100}%]",
                f"Trade Name: '{trade_name}'",
                f"Is Distributor: {is_distributor}"
            ],
            extracted_data={
                "manufacturer_name": mfr_name,
                "brand_name": brand_name,
                "trade_name": trade_name,
                "mfr_part_number": mpn,
                "alternate_part_number": alt_mpn
            }
        )

        return {
            "manufacturer_name": mfr_name,
            "brand_name": brand_name,
            "trade_name": trade_name,
            "mfr_part_number": mpn,
            "alt_part_number": alt_mpn,
            "brand_confidence": conf,
            "traces": state.traces + [trace]
        }
