import time
import re
import os
from typing import Dict, Any, Tuple
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..db.duckdb_client import kb
from ..core.logging import logger

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    HAS_OPENAI = False


class EntityResolutionAgent:
    """
    Agent 2: Brand & Entity Resolution Agent
    Resolves noisy supplier strings and description tokens to canonical UniCat 27K
    Manufacturers and Brands with legal casing and mandatory registered marks (®, ™).
    Checks active human reviewer feedback overrides first, then uses in-memory DuckDB lookups
    and falls back to OpenAI GPT-4o-mini for unseen complex feeds.
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
        "ADCR": "AZEK",
        "DWS": "DEWALT",
        "DCD": "DEWALT",
        "DCF": "DEWALT",
        "XPH": "MAKITA",
        "XDT": "MAKITA"
    }

    # Vendor / Distributor Code -> Canonical OEM / Brand hints
    VENDOR_CODE_TO_OEM_MAP = {
        "5831": ("Signify North America Corporation", "Philips®"),
        "KICLI": ("Kichler Lighting LLC", "Kichler®"),
        "5573": ("Satco Products Inc", "Satco®"),
        "2585": ("Stanley Black & Decker Inc", "DEWALT®"),
        "5142": ("Makita U.S.A. Inc", "Makita®"),
        "FESTO": ("Festool USA Inc", "Festool®"),
        "4927": ("Leviton Manufacturing Co Inc", "Leviton®"),
        "6603": ("Southwire Company LLC", "Southwire®"),
        "4031": ("Milwaukee Electric Tool Corporation", "Milwaukee®"),
        "MIRUS": ("Mirka USA Inc", "Mirka®"),
        "2435": ("Freud America Inc", "Diablo®"),
        "6151": ("The AZEK Company LLC", "TimberTech®"),
        "3073": ("Trex Company Inc", "Trex®")
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
        "Transcend": "Transcend",
        "Select 2.0": "Select 2.0",
        "Lineage": "Lineage",
        "Vintage": "Vintage",
        "Landmark": "Landmark",
        "Harvest": "Harvest",
        "Professional": "Professional Series",
        "Eco": "Eco Series",
        "SmartSide": "SmartSide®",
        "HardiePlank": "HardiePlank®"
    }

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        desc_text = state.cleaned_part_desc or ""
        supp_name = state.clean_supplier_name or ""
        vendor_code = (state.supplier_vendor_code or "").upper()
        mpn = (state.clean_mfg_part_num or "").strip()

        # Step 0: Check Active Reviewer Overrides Store (HITL Feedback Loop)
        override = kb.get_override(mpn)
        if override and override.get("brand_name"):
            mfr_name = override.get("manufacturer_name", "")
            brand_name = override.get("brand_name", "")
            conf = 1.0
            trade_name = override.get("trade_name", "")
            alt_mpn = mpn.replace("-", "").replace(".", "").strip()
            if alt_mpn == mpn:
                alt_mpn = ""

            trace = AgentTrace(
                agent_name="Agent 2: Brand & Entity Resolution",
                execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
                notes=[
                    f"Applied Active Reviewer Override: '{brand_name}' ({mfr_name})",
                    f"Reviewer notes: {override.get('reviewer_notes', 'Approved by human specialist')}"
                ],
                extracted_data={
                    "manufacturer_name": mfr_name,
                    "brand_name": brand_name,
                    "trade_name": trade_name,
                    "mfr_part_number": mpn,
                    "alternate_part_number": alt_mpn,
                    "active_override_applied": True
                }
            )
            return {
                "manufacturer_name": mfr_name,
                "brand_name": brand_name,
                "trade_name": trade_name,
                "mfr_part_number": mpn,
                "alt_part_number": alt_mpn,
                "brand_confidence": 1.0,
                "traces": state.traces + [trace]
            }

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
            if cand_u in cls.DISTRIBUTOR_MAP or any(d.upper() in cand_u for d in cls.DISTRIBUTOR_MAP.values()):
                continue
            brand_match = kb.find_brand(cand)
            if brand_match:
                break

        # Step 4: Priority 2 - Check Vendor Code OEM Map
        if not brand_match and vendor_code in cls.VENDOR_CODE_TO_OEM_MAP:
            mfr_name, brand_name = cls.VENDOR_CODE_TO_OEM_MAP[vendor_code]
            conf = 1.0

        # Step 5: Priority 3 - Check MPN Prefix Map
        if not brand_match and not mfr_name and mpn:
            for prefix, mapped_brand in cls.MPN_PREFIX_MAP.items():
                if mpn.upper().startswith(prefix):
                    brand_match = kb.find_brand(mapped_brand)
                    if brand_match:
                        break

        # Step 6: Priority 4 - Search Description Words for Known Brands
        if not brand_match and not mfr_name and desc_text:
            desc_words = desc_text.split()
            for w in desc_words:
                clean_w = re.sub(r"[^A-Za-z0-9]", "", w)
                if len(clean_w) >= 2:
                    brand_match = kb.find_brand(clean_w)
                    if brand_match:
                        break

        # Step 7: Priority 5 - If supplier is NOT a distributor, match supplier name
        if not brand_match and not mfr_name and not is_distributor and supp_name:
            brand_match = kb.find_brand(supp_name)

        # Step 8: Assign canonical results if matched from DuckDB
        if brand_match:
            mfr_name, brand_name, conf = brand_match
        elif not mfr_name:
            if supp_name and not is_distributor:
                mfr_name = supp_name
                brand_name = supp_name
                conf = 0.70
            else:
                mfr_name = supp_name or "Unassigned Manufacturer"
                brand_name = supp_name or "Unbranded"
                conf = 0.40

        # Step 9: Optional OpenAI LLM Disambiguator if confidence is low and enabled
        openai_used = False
        openai_time_ms = 0.0
        if conf < 0.75 and HAS_OPENAI and state.enable_llm and desc_text:
            try:
                t_ai_0 = time.perf_counter()
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                prompt = (
                    f"Disambiguate the true OEM Manufacturer and Brand for raw supplier: '{supp_name}', MPN: '{mpn}', Desc: '{desc_text}'.\n"
                    "Output in exact format: MFR: <Legal Manufacturer Name> | BRAND: <Brand Name with ® or ™>"
                )
                res = llm.invoke([
                    SystemMessage(content="You are an expert industrial master catalog data entity resolver."),
                    HumanMessage(content=prompt)
                ])
                openai_time_ms = round((time.perf_counter() - t_ai_0) * 1000, 2)
                content = res.content.strip()
                m_match = re.search(r"MFR:\s*([^|]+)\|\s*BRAND:\s*(.+)", content)
                if m_match:
                    ai_mfr = m_match.group(1).strip()
                    ai_brand = m_match.group(2).strip()
                    kb_check = kb.find_brand(ai_brand)
                    if kb_check:
                        mfr_name, brand_name, conf = kb_check
                    else:
                        mfr_name = ai_mfr
                        brand_name = ai_brand
                        conf = 0.88
                    openai_used = True
            except Exception as e:
                logger.warning(f"OpenAI entity resolution fallback used standard match: {e}")

        # Step 10: Alternate Part Number derivation
        alt_mpn = mpn.replace("-", "").replace(".", "").strip()
        if alt_mpn == mpn:
            alt_mpn = ""

        trace = AgentTrace(
            agent_name="Agent 2: Brand & Entity Resolution",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Resolved: '{brand_name}' ({mfr_name}) [Score: {conf*100}%]",
                f"Trade Name: '{trade_name}'",
                f"Is Distributor: {is_distributor}",
                f"OpenAI Disambiguated: {openai_used}" + (f" ({openai_time_ms} ms)" if openai_used else "")
            ],
            extracted_data={
                "manufacturer_name": mfr_name,
                "brand_name": brand_name,
                "trade_name": trade_name,
                "mfr_part_number": mpn,
                "alternate_part_number": alt_mpn,
                "openai_used": openai_used,
                "openai_time_ms": openai_time_ms
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
