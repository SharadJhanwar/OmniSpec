import time
import re
import os
from typing import Dict, Any, Tuple
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..db.duckdb_client import kb
from ..core.logging import logger
from ..core.config import settings
from ..services.evidence_discovery_service import EvidenceDiscoveryService

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY)
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

    # Trade name patterns for product lines
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

        desc_text = state.cleaned_part_desc or state.raw_part_desc or ""
        supp_name = state.clean_supplier_name or state.raw_e1_brand or state.raw_part_manuf or ""
        if supp_name.strip().lower() in ["-- unbranded --", "unbranded", "no brand", "-- no unilog brand --", "-- no dib brand --", "n/a", "none", "unassigned", ""]:
            supp_name = ""
        vendor_code = (state.supplier_vendor_code or "").upper()
        mpn = (state.clean_mfg_part_num or state.raw_mfg_part_num or "").strip()

        # Step 0: Check Active Reviewer Overrides Store (Approved Human Knowledge from HITL)
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

        # Step 2: Exact / Fuzzy KB Retrieval from DuckDB (unicat_brands)
        brand_match = None

        # Priority A: Check explicit brand candidates from feed
        brand_candidates = state.token_bag.get("brand_candidates", [])
        for cand in brand_candidates:
            if cand and len(cand) >= 2:
                brand_match = kb.find_brand(cand)
                if brand_match:
                    break

        # Priority B: Search description tokens in DuckDB
        if not brand_match and desc_text:
            desc_words = desc_text.split()
            for w in desc_words:
                clean_w = re.sub(r"[^A-Za-z0-9]", "", w)
                if len(clean_w) >= 2:
                    brand_match = kb.find_brand(clean_w)
                    if brand_match:
                        break

        # Priority C: Search supplier name in DuckDB
        if not brand_match and supp_name:
            brand_match = kb.find_brand(supp_name)

        # Priority D: Search vendor code token in DuckDB
        if not brand_match and vendor_code:
            brand_match = kb.find_brand(vendor_code)

        # Priority E: Search MPN token in DuckDB
        if not brand_match and mpn:
            brand_match = kb.find_brand(mpn)

        # Step 3: Check if resolved with high confidence from KB
        if brand_match:
            mfr_name, brand_name, conf = brand_match
        elif supp_name:
            # Clean supplier string into manufacturer and brand candidates
            clean_supp = re.sub(r"\s*\([A-Za-z0-9_-]+\)$", "", supp_name).strip()
            mfr_name = clean_supp
            brand_name = clean_supp
            conf = 0.70
        else:
            mfr_name = "Unassigned Manufacturer"
            brand_name = "Unbranded"
            conf = 0.40
        openai_used = False
        openai_time_ms = 0.0
        has_openai = bool(os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY)
        if conf < 0.75 and has_openai and state.enable_llm and (desc_text or mpn):
            try:
                t_ai_0 = time.perf_counter()
                
                # Fetch live web evidence via DuckDuckGo to discover true OEM
                web_ev = EvidenceDiscoveryService.discover_web_evidence(
                    mpn=mpn,
                    desc=desc_text,
                    max_results=3
                )
                ev_snippets = [f"- {e.get('title')}: {e.get('snippet')}" for e in web_ev]
                evidence_str = "\n".join(ev_snippets) if ev_snippets else "No web evidence retrieved."

                api_k = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
                llm = ChatOpenAI(api_key=api_k, model="gpt-4o-mini", temperature=0)
                prompt = (
                    f"INPUT SKU:\n- Supplier: '{supp_name}'\n- MPN: '{mpn}'\n- Desc: '{desc_text}'\n\n"
                    f"LIVE WEB EVIDENCE / TECHNICAL SEARCH SNIPPETS:\n{evidence_str}\n\n"
                    "Identify the true legal OEM Manufacturer and Brand name from the evidence.\n"
                    "If truly unknown / unbranded, return MFR: -- Unbranded -- | BRAND: -- Unbranded --\n"
                    "Output in exact format: MFR: <Legal Manufacturer Name> | BRAND: <Brand Name with ® or ™ if known>"
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
                    if ai_brand not in ["-- Unbranded --", "Unbranded", ""]:
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
