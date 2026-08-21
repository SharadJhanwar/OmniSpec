import time
import re
import os
from typing import Dict, Any, Tuple, Optional
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..db.duckdb_client import kb
from ..core.logging import logger

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    HAS_OPENAI = False


class TaxonomyClassifierAgent:
    """
    Agent 3: Dynamic Taxonomy & UNSPSC Classifier Agent
    Uses hybrid keyword + fuzzy retrieval over DuckDB unicat_taxonomy_nodes
    with structured LLM zero-shot ranking for ambiguous novel items.
    Eliminates all hardcoded category lambda arrays.
    """

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        desc_text = state.cleaned_part_desc or ""
        mpn = (state.clean_mfg_part_num or "").strip()

        # Step 0: Check Active Reviewer Overrides Store (HITL Approved Knowledge)
        override = kb.get_override(mpn)
        if override and override.get("classpath"):
            cp_meta = kb.get_taxonomy_by_classpath(override["classpath"]) or {}
            classpath = override["classpath"]
            dept = override.get("dept") or cp_meta.get("dept", "General")
            class_name = override.get("class_name") or cp_meta.get("class_name", "General")
            fine = override.get("fine") or cp_meta.get("fine_name", "General")
            product_name = override.get("product_name") or cp_meta.get("product_name", "Product")
            unspsc = override.get("unspsc") or cp_meta.get("unspsc", "31160000")
            conf = 1.0

            active_lov_schema = kb.get_lov_schema(classpath)
            trace = AgentTrace(
                agent_name="Agent 3: Dynamic Taxonomy & Classification",
                execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
                notes=[
                    f"Applied Active Reviewer Taxonomy Override: '{classpath}' [UNSPSC: {unspsc}]",
                    f"Product Name: '{product_name}'"
                ],
                extracted_data={
                    "classpath": classpath,
                    "dept": dept,
                    "class_name": class_name,
                    "fine": fine,
                    "product_name": product_name,
                    "unspsc": unspsc,
                    "active_override_applied": True
                }
            )
            return {
                "classpath": classpath,
                "dept": dept,
                "class_name": class_name,
                "fine": fine,
                "product_name": product_name,
                "unspsc": unspsc,
                "taxonomy_confidence": conf,
                "traces": state.traces + [trace]
            }

        # Step 1: Hybrid Retrieval from DuckDB (unicat_taxonomy_nodes)
        candidates = kb.search_taxonomy(desc_text, top_k=5)
        
        classpath = ""
        dept = ""
        class_name = ""
        fine = ""
        product_name = ""
        unspsc = ""
        conf = 0.0
        llm_used = False

        if candidates and candidates[0]["score"] >= 35.0:
            top = candidates[0]
            classpath = top["classpath"]
            dept = top["dept"]
            class_name = top["class_name"]
            fine = top["fine_name"]
            product_name = top["product_name"]
            unspsc = top["unspsc"]
            conf = min(0.98, top["confidence"])
        elif candidates:
            # Step 2: Structured LLM Zero-Shot Reasoning if retrieval confidence is ambiguous
            if HAS_OPENAI and state.enable_llm:
                try:
                    t_ai_0 = time.perf_counter()
                    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                    options_str = "\n".join([f"- {c['classpath']} | UNSPSC: {c['unspsc']} | Product: {c['product_name']}" for c in candidates])
                    prompt = (
                        f"Given product description: '{desc_text}', MPN: '{mpn}'.\n"
                        f"Select the best matching taxonomy classification from the candidates below, or propose canonical classification.\n"
                        f"Candidates:\n{options_str}\n\n"
                        "Format Output: CLASSPATH: <path> | UNSPSC: <8-digit> | PRODUCT_NAME: <name> | DEPT: <dept> | CLASS: <class> | FINE: <fine>"
                    )
                    res = llm.invoke([
                        SystemMessage(content="You are an industrial catalog master taxonomist."),
                        HumanMessage(content=prompt)
                    ])
                    content = res.content.strip()
                    m = re.search(r"CLASSPATH:\s*([^|]+)\|\s*UNSPSC:\s*(\d+)\|\s*PRODUCT_NAME:\s*([^|]+)\|\s*DEPT:\s*([^|]+)\|\s*CLASS:\s*([^|]+)\|\s*FINE:\s*(.+)", content)
                    if m:
                        classpath = m.group(1).strip()
                        unspsc = m.group(2).strip()
                        product_name = m.group(3).strip()
                        dept = m.group(4).strip()
                        class_name = m.group(5).strip()
                        fine = m.group(6).strip()
                        conf = 0.90
                        llm_used = True
                except Exception as e:
                    logger.warning(f"OpenAI taxonomy classification fallback used top candidate: {e}")

            if not classpath:
                top = candidates[0]
                classpath = top["classpath"]
                dept = top["dept"]
                class_name = top["class_name"]
                fine = top["fine_name"]
                product_name = top["product_name"]
                unspsc = top["unspsc"]
                conf = 0.65
        else:
            # Fallback General Classification
            classpath = "Industrial Supplies & Hardware>General Hardware"
            dept = "Hardware"
            class_name = "General"
            fine = "Industrial Hardware"
            product_name = "Industrial Component"
            unspsc = "31160000"
            conf = 0.40

        # Retrieve active LOV attribute schema from DuckDB for the assigned classpath
        active_lov_schema = kb.get_lov_schema(classpath)

        trace = AgentTrace(
            agent_name="Agent 3: Dynamic Taxonomy & Classification",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Assigned Classpath: '{classpath}' [UNSPSC: {unspsc}]",
                f"Product Name: '{product_name}' (Confidence: {conf*100}%)",
                f"LLM Classification Invoked: {llm_used}",
                f"Loaded {len(active_lov_schema)} active LOV schema attributes"
            ],
            extracted_data={
                "classpath": classpath,
                "dept": dept,
                "class_name": class_name,
                "fine": fine,
                "product_name": product_name,
                "unspsc": unspsc,
                "taxonomy_confidence": conf,
                "llm_used": llm_used,
                "active_schema_count": len(active_lov_schema)
            }
        )

        return {
            "classpath": classpath,
            "dept": dept,
            "class_name": class_name,
            "fine": fine,
            "product_name": product_name,
            "unspsc": unspsc,
            "taxonomy_confidence": conf,
            "traces": state.traces + [trace]
        }
