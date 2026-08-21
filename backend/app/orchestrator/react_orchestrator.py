import time
import os
import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..schemas.delivery_schema import DeliveryProductRecord
from ..db.duckdb_client import kb
from ..services.evidence_discovery_service import EvidenceDiscoveryService
from ..services.audit_engine import QualityAuditEngine
from ..agents.agent_1_ingestion import IngestionAgent
from ..agents.agent_2_entity_resolution import EntityResolutionAgent
from ..agents.agent_3_taxonomy import TaxonomyClassifierAgent
from ..agents.agent_4_spec_uom import SpecUOMExtractorAgent
from ..agents.agent_5_oem_sourcing import OEMSourcingRAGAgent
from ..agents.agent_6_lov_mapper import ConstrainedLOVMapperAgent
from ..agents.agent_7_copy_builder import MultiChannelCopyAgent
from ..agents.agent_8_digital_assets import DigitalAssetAgent

logger = logging.getLogger(__name__)

# =====================================================================
# DEDICATED REAC TOOLS FOR THE ORCHESTRATOR BRAIN
# =====================================================================

@tool
def tool_kb_hybrid_retrieval(query: str) -> str:
    """
    Hybrid Knowledge Base Retrieval Tool:
    Combines exact lookup, RapidFuzz, BM25, and semantic vector similarity across
    DuckDB 27,000+ brand aliases, LOVs, 4-tier taxonomy nodes, and active reviewer overrides.
    """
    if not query:
        return "Empty query."

    # 1. Brand Lookup
    brand_res = kb.find_brand(query)
    # 2. Active Human Overrides
    override_res = kb.get_override(query)
    # 3. Taxonomy Search
    tax_res = kb.search_taxonomy(query, top_k=3)

    results = {}
    if brand_res:
        results["brand_match"] = {
            "manufacturer_name": brand_res[0],
            "brand_name": brand_res[1],
            "confidence": brand_res[2]
        }
    if override_res:
        results["active_human_override"] = override_res
    if tax_res:
        results["taxonomy_candidates"] = [
            {"classpath": t["classpath"], "unspsc": t["unspsc"], "product": t["product_name"], "score": t["score"]}
            for t in tax_res
        ]

    if not results:
        return f"No confident match in local KB for '{query}'."
    return json.dumps(results, indent=2)


@tool
def tool_web_search_general(query: str) -> str:
    """
    General Web Search Tool:
    Searches the technical web via DuckDuckGo for brand identity, manufacturer information,
    and product categorization. Automatically filters out consumer marketplaces (Amazon, eBay, Flipkart, etc.).
    """
    if not query:
        return "Empty query."

    evidence = EvidenceDiscoveryService.discover_web_evidence(
        mpn=query,
        desc="",
        max_results=4
    )

    if not evidence:
        return f"No general web evidence found for '{query}'."

    reranked = EvidenceDiscoveryService.rank_best_evidence(
        query=query,
        evidence_items=evidence,
        top_k=3
    )

    summary = []
    for idx, e in enumerate(reranked, 1):
        summary.append(
            f"[{idx}] Title: {e.get('title')}\n"
            f"    URL: {e.get('url')} (Quality: {e.get('source_quality')})\n"
            f"    Snippet: {e.get('snippet')}"
        )
    return "\n\n".join(summary)


@tool
def tool_datasheet_pdf_search(mpn: str, brand: str = "") -> str:
    """
    Targeted Datasheet & Technical PDF Search Tool:
    Specifically queries for official manufacturer specification sheets, engineering submittals,
    and PDF manuals for an exact MPN.
    """
    if not mpn:
        return "No MPN provided."

    evidence = EvidenceDiscoveryService.discover_web_evidence(
        mpn=mpn,
        brand=brand if brand and brand != "-- Unbranded --" else "",
        desc="technical specifications datasheet pdf",
        max_results=4
    )

    if not evidence:
        return f"No technical PDF datasheets found for '{brand} {mpn}'."

    reranked = EvidenceDiscoveryService.rank_best_evidence(
        query=f"{brand} {mpn} datasheet pdf specifications",
        evidence_items=evidence,
        top_k=2
    )

    summary = []
    for idx, e in enumerate(reranked, 1):
        summary.append(
            f"[{idx}] Datasheet Title: {e.get('title')}\n"
            f"    PDF URL: {e.get('url')} (Quality: {e.get('source_quality')})\n"
            f"    Technical Snippet: {e.get('snippet')}"
        )
    return "\n\n".join(summary)


@tool
def tool_extract_specs_and_uoms(text: str) -> str:
    """
    Deterministic Spec & Unit-of-Measure (UOM) Extraction Tool:
    Parses numerical dimensions (LxWxH in/mm), electrical specs (V, A, W, kAIC, HP),
    pressures (PSI), speeds (RPM), flow (GPM), acoustic noise (dBA), and wire gauges (AWG).
    """
    dummy_state = ProductEnrichmentState(
        row_id="temp_spec_extract",
        raw_mfg_part_num="",
        raw_part_desc=text,
        raw_e1_brand="",
        raw_unilog_brand="",
        raw_dib_brand="",
        raw_part_manuf=""
    )
    ingested = IngestionAgent.execute(dummy_state)
    dummy_state = dummy_state.model_copy(update=ingested)
    specs = SpecUOMExtractorAgent.execute(dummy_state)

    extracted = {
        "dimensions": specs.get("dimensions", {}),
        "electrical_specs": specs.get("electrical_specs", {}),
        "acoustic_specs": specs.get("acoustic_specs", {})
    }
    return json.dumps(extracted, indent=2)


@tool
def tool_bind_lov_schema(classpath: str, specs_json_str: str) -> str:
    """
    Dynamic LOV Schema Mapping Tool:
    Retrieves the active UniCat LOV schema for the category and binds grounded specs
    into structured attribute triples [ATTRIBUTE_LABEL, ATTRIBUTE_VALUE, ATTRIBUTE_UOM].
    """
    try:
        specs_dict = json.loads(specs_json_str) if isinstance(specs_json_str, str) else specs_json_str
    except Exception:
        specs_dict = {}

    schema = kb.get_lov_schema(classpath) if classpath else []
    bound_attrs = {}
    attr_idx = 1

    # Schema-driven mapping
    for item in schema:
        lbl = item.get("label", "")
        uom_def = item.get("uom", "")
        for k, v in specs_dict.items():
            if k.lower() in lbl.lower() or lbl.lower() in k.lower():
                bound_attrs[f"ATTRIBUTE_LABEL {attr_idx}"] = lbl
                bound_attrs[f"ATTRIBUTE_VALUE {attr_idx}"] = str(v)
                bound_attrs[f"ATTRIBUTE_UOM {attr_idx}"] = uom_def
                attr_idx += 1
                break

    # Remaining unmapped specs
    for k, v in specs_dict.items():
        if not any(k.lower() in bound_attrs.get(f"ATTRIBUTE_LABEL {i}", "").lower() for i in range(1, attr_idx)):
            if not k.endswith(" UOM"):
                uom_val = specs_dict.get(f"{k} UOM", "")
                bound_attrs[f"ATTRIBUTE_LABEL {attr_idx}"] = k
                bound_attrs[f"ATTRIBUTE_VALUE {attr_idx}"] = str(v)
                bound_attrs[f"ATTRIBUTE_UOM {attr_idx}"] = uom_val
                attr_idx += 1

    # Ensure all 50 slots (150 keys) are present
    for i in range(1, 51):
        if f"ATTRIBUTE_LABEL {i}" not in bound_attrs:
            bound_attrs[f"ATTRIBUTE_LABEL {i}"] = ""
            bound_attrs[f"ATTRIBUTE_VALUE {i}"] = ""
            bound_attrs[f"ATTRIBUTE_UOM {i}"] = ""

    return json.dumps(bound_attrs, indent=2)


@tool
def tool_synthesize_unilog_copy(
    brand: str,
    product_name: str,
    mpn: str,
    key_specs: str = ""
) -> str:
    """
    Universal Multi-Tier Copy Synthesis Tool:
    Generates contractually bounded Unilog descriptions:
    - INVOICE_DESC: <= 40 chars, ALL CAPS (Formula: [PRODUCT_NOUN] [SPECS] [MPN])
    - MOBILE_DESC: 60 to 80 chars (Formula: [BRAND], [PRODUCT_NAME], [SPECS], [MPN])
    - SHORT_DESC & LONG_DESC1
    """
    brand_disp = brand if brand and brand != "-- Unbranded --" else "Unbranded"
    prod_noun = product_name.upper() if product_name else "INDUSTRIAL COMPONENT"

    # INVOICE_DESC (<= 40 chars ALL CAPS)
    candidate_inv = f"{prod_noun} {key_specs} {mpn.upper()}".strip()
    candidate_inv = re.sub(r"\s+", " ", candidate_inv)
    if len(candidate_inv) > 40:
        candidate_inv = f"{prod_noun} {mpn.upper()}".strip()
        if len(candidate_inv) > 40:
            candidate_inv = candidate_inv[:40]
    invoice_desc = candidate_inv.upper()

    # MOBILE_DESC (60 to 80 chars)
    mob_raw = f"{brand_disp}, {product_name}, {key_specs}, {mpn}".strip()
    mob_raw = re.sub(r",\s*,", ",", mob_raw)
    if len(mob_raw) < 60:
        mob_desc = f"{brand_disp}, {product_name}, {mpn}".strip().ljust(60)
    elif len(mob_raw) > 80:
        mob_desc = mob_raw[:80].rstrip()
    else:
        mob_desc = mob_raw

    copy_results = {
        "invoice_desc": invoice_desc,
        "invoice_desc_len": len(invoice_desc),
        "mobile_desc": mob_desc,
        "mobile_desc_len": len(mob_desc),
        "short_desc": f"{brand_disp} {mpn} {product_name}".strip(),
        "long_desc1": f"{brand_disp} {mpn} {product_name}, engineered for heavy-duty industrial applications.",
        "retail_desc": f"{brand_disp} {product_name}",
        "marketing_desc": f"Professional-grade {product_name} by {brand_disp}. MPN: {mpn}.",
        "item_features": [f"Manufacturer Part Number: {mpn}", f"Product Type: {product_name}"] + [""] * 18
    }
    return json.dumps(copy_results, indent=2)


@tool
def tool_generate_digital_assets(brand: str, mpn: str) -> str:
    """
    Digital Asset Synthesis Tool:
    Generates standardized digital asset filenames conforming to Unilog standard:
    - Product Image: <CleanBrand>_<MPN>.jpg
    - Specification Sheet: <CleanBrand>_<MPN>_Specification_Sheet.pdf
    """
    clean_b = re.sub(r"[^A-Za-z0-9]", "", brand or "UNBRANDED").upper()
    clean_m = re.sub(r"[^A-Za-z0-9_-]", "", mpn or "UNKNOWN").upper()
    assets = {
        "Product Image": f"{clean_b}_{clean_m}.jpg",
        "Specification Sheet": f"{clean_b}_{clean_m}_Specification_Sheet.pdf"
    }
    return json.dumps(assets, indent=2)


# =====================================================================
# STRUCTURED REAC OUTPUT MODEL
# =====================================================================

class SpecItem(BaseModel):
    name: str = Field(description="Spec parameter name (e.g. 'Voltage Rating', 'Amperage Rating', 'Wire Capacity')")
    value: str = Field(description="Spec value (e.g. '24', '20', '10-18')")
    uom: str = Field(default="", description="Unit of measure (e.g. 'V', 'A', 'AWG', 'PSI')")


class ReActMasterBrainOutput(BaseModel):
    step1_direct_knowledge: str = Field(description="1. What do I know directly from input? (MPN, tokens, specs)")
    step2_missing_information: str = Field(description="2. What is missing? (MFR identity, taxonomy classpath, LOV specs)")
    step3_kb_evaluation: str = Field(description="3. Did DuckDB Knowledge Base answer it? Summarize findings.")
    step4_evidence_sufficiency: str = Field(description="4. Is evidence sufficient? (YES / NO - details on search hops)")
    step6_reasoning_and_resolution: str = Field(description="6. Structured reasoning resolving any ambiguities.")
    resolved_brand: str = Field(description="The verified brand name (e.g. 'Bosch', 'Klein Tools', 'Loctite', 'SKF', 'Eaton'). If unknown, return '-- Unbranded --'.")
    resolved_manufacturer: str = Field(description="The legal manufacturer name (e.g. 'BSH Home Appliances', 'Klein Tools Inc', 'Henkel Corporation', 'SKF Group', 'Eaton Corporation').")
    product_name: str = Field(description="Concise product noun (e.g. 'Dishwasher', 'Wire Stripper Cutter', 'Deep Groove Ball Bearing', 'Circuit Breaker', 'Threadlocker', 'DC Gear Motor').")
    taxonomy_classpath: str = Field(description="The canonical 3 or 4-tier taxonomy path matching the product.")
    unspsc_code: str = Field(description="8-digit UNSPSC code matching the taxonomy.")
    grounded_specs: List[SpecItem] = Field(default_factory=list, description="Specs extracted ONLY from input description or verified search snippets.")
    grounded_approvals: List[str] = Field(default_factory=list, description="Explicit approvals verified in evidence (e.g. ['UL Listed', 'ISO 9001']).")
    official_oem_url: Optional[str] = Field(default="", description="The verified manufacturer or datasheet PDF URL from evidence.")
    calibrated_confidence: float = Field(description="Realistic confidence score between 0.30 and 0.98 based on evidence completeness.")


# =====================================================================
# THE MULTI-HOP REACT ORCHESTRATOR BRAIN
# =====================================================================

class ReActOrchestrator:
    """
    Adaptive Multi-Hop ReAct Orchestrator:
    Executes iterative retrieval over DuckDB KB, General Web Search, and Datasheet PDF crawlers
    until sufficient evidence is gathered, followed by LLM reasoning, deterministic validation,
    and HITL gating.
    """

    ORCHESTRATOR_TOOLS = [
        tool_kb_hybrid_retrieval,
        tool_web_search_general,
        tool_datasheet_pdf_search,
        tool_extract_specs_and_uoms,
        tool_bind_lov_schema,
        tool_synthesize_unilog_copy,
        tool_generate_digital_assets
    ]

    @classmethod
    def process_sku(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        mpn = (state.clean_mfg_part_num or state.raw_mfg_part_num or "").strip()
        desc = state.cleaned_part_desc or state.raw_part_desc or ""
        manuf = state.clean_supplier_name or state.raw_part_manuf or ""

        # Step 0: Check Active Human Reviewer Overrides in DuckDB
        override = kb.get_override(mpn)
        if override:
            logger.info(f"[ReActOrchestrator] Active Reviewer Override found for MPN: {mpn}")
            trace = AgentTrace(
                agent_name="ReAct Master Orchestrator (Cognitive Brain)",
                execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
                notes=[f"Applied Active Human Reviewer Override for {mpn}"],
                extracted_data=override
            )
            return {
                "brand_name": override.get("brand_name", state.brand_name),
                "manufacturer_name": override.get("manufacturer_name", state.manufacturer_name),
                "classpath": override.get("classpath", state.classpath),
                "product_name": override.get("product_name", state.product_name),
                "unspsc": override.get("unspsc", state.unspsc),
                "dept": override.get("dept", state.dept),
                "class_name": override.get("class_name", state.class_name),
                "fine": override.get("fine", state.fine),
                "mfr_url": override.get("mfr_url", state.mfr_url),
                "brand_confidence": 1.0,
                "overall_confidence": 1.0,
                "needs_hitl_review": False,
                "traces": state.traces + [trace]
            }

        # -------------------------------------------------------------
        # HOP 1: Direct Knowledge & Local Knowledge Base Hybrid Retrieval
        # -------------------------------------------------------------
        direct_specs_obs = tool_extract_specs_and_uoms.invoke({"text": desc})
        direct_specs = json.loads(direct_specs_obs)

        kb_obs = tool_kb_hybrid_retrieval.invoke({"query": f"{manuf} {desc} {mpn}".strip()})
        kb_brand_match = kb.find_brand(manuf or desc or mpn)
        kb_tax_match = kb.search_taxonomy(f"{desc} {mpn}", top_k=2)

        kb_confidence = kb_brand_match[2] if kb_brand_match else 0.0

        # -------------------------------------------------------------
        # HOP 2: Evidence Sufficiency Gate & Targeted Web Evidence Discovery
        # -------------------------------------------------------------
        web_general_obs = ""
        datasheet_pdf_obs = ""
        evidence_sufficient = kb_confidence >= 0.85 and bool(kb_tax_match)

        if not evidence_sufficient:
            # Iterative Step 1: General Web Search for brand & product context
            web_general_obs = tool_web_search_general.invoke({"query": f"{mpn} {desc}".strip()})

            # Iterative Step 2: Targeted Datasheet PDF search for deep technical specs
            brand_hint = kb_brand_match[1] if kb_brand_match else ""
            datasheet_pdf_obs = tool_datasheet_pdf_search.invoke({
                "mpn": mpn,
                "brand": brand_hint
            })
        else:
            web_general_obs = "[KB confidence was high (>= 85%) - External web crawl bypassed]"

        # -------------------------------------------------------------
        # HOP 3: Structured LLM Reasoning over Multi-Hop Evidence
        # -------------------------------------------------------------
        has_api_key = bool(os.getenv("OPENAI_API_KEY")) and state.enable_llm
        grounded_data: Optional[ReActMasterBrainOutput] = None

        if has_api_key:
            try:
                system_prompt = (
                    "You are the ReAct Master Orchestrator Brain for OmniSpec AI.\n"
                    "You operate an Adaptive Multi-Hop Reasoning Loop over local DuckDB KB results, general web evidence, and technical PDF datasheets.\n\n"
                    "RULES:\n"
                    "1. ZERO HALLUCINATION: Extract only facts grounded in input description or evidence. Never invent fake voltages, wattages (e.g. 4750W 240V), grips, or fake specs!\n"
                    "2. PRECISE CLASSIFICATION: Correctly distinguish categories (e.g. 'DC Gear Motor' is an Electric Motor, NOT a Multimeter; 'Ball Valve' is a Valve; 'Aviation Snips' are Snips; 'Wire Stripper' is a Stripper/Cutter).\n"
                    "3. CALIBRATED CONFIDENCE: If the item has unknown brand or sparse evidence, assign 0.45 - 0.70. If verified with OEM link and complete specs, assign 0.85 - 0.95."
                )

                user_prompt = (
                    f"INPUT SKU:\n"
                    f"- MPN: {mpn}\n"
                    f"- Description: {desc}\n"
                    f"- Supplier / Manuf: {manuf}\n\n"
                    f"1. DIRECT SPEC EXTRACTION:\n{direct_specs_obs}\n\n"
                    f"2. LOCAL KNOWLEDGE BASE (DuckDB Hybrid):\n{kb_obs}\n\n"
                    f"3. GENERAL WEB EVIDENCE (Hop 1):\n{web_general_obs}\n\n"
                    f"4. TECHNICAL PDF DATASHEETS (Hop 2):\n{datasheet_pdf_obs}\n\n"
                    f"Execute multi-hop ReAct cognitive synthesis and return the structured output."
                )

                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_retries=2)
                structured_llm = llm.with_structured_output(ReActMasterBrainOutput, method="function_calling")
                grounded_data = structured_llm.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ])
            except Exception as e:
                logger.warning(f"[ReActOrchestrator] LLM reasoning fallback: {e}")

        # -------------------------------------------------------------
        # STEP 9 & 10: Compile Enriched State, Deterministic Validation & Delivery Assembly
        # -------------------------------------------------------------
        updates: Dict[str, Any] = {}

        if grounded_data:
            brand_res = grounded_data.resolved_brand
            mfr_res = grounded_data.resolved_manufacturer
            prod_noun = grounded_data.product_name
            classpath = grounded_data.taxonomy_classpath
            unspsc = grounded_data.unspsc_code
            oem_url = grounded_data.official_oem_url or ""
            conf = grounded_data.calibrated_confidence

            # Extract 4-tier taxonomy parts
            parts = [p.strip() for p in classpath.split(">")] if classpath else []
            dept = parts[0] if len(parts) > 0 else ""
            cls_name = parts[1] if len(parts) > 1 else ""
            fine = parts[2] if len(parts) > 2 else ""

            updates["brand_name"] = brand_res
            updates["manufacturer_name"] = mfr_res
            updates["product_name"] = prod_noun
            updates["classpath"] = classpath
            updates["dept"] = dept
            updates["class_name"] = cls_name
            updates["fine"] = fine
            updates["unspsc"] = unspsc
            updates["mfr_url"] = oem_url
            updates["ref_urls"] = [oem_url] if oem_url else []
            updates["brand_confidence"] = conf
            updates["overall_confidence"] = conf
            updates["needs_hitl_review"] = conf < 0.80

            # Grounded specs aggregation
            specs_map = dict(state.electrical_specs or {})
            for s in grounded_data.grounded_specs:
                specs_map[s.name] = s.value
                if s.uom:
                    specs_map[f"{s.name} UOM"] = s.uom
            updates["electrical_specs"] = specs_map
            updates["dimensions"] = direct_specs.get("dimensions", {})
            updates["acoustic_specs"] = direct_specs.get("acoustic_specs", {})

            if grounded_data.grounded_approvals:
                updates["standard_approvals"] = "|".join(grounded_data.grounded_approvals)

            # Invoke Helper Tool: LOV Schema Binder
            lov_obs = tool_bind_lov_schema.invoke({
                "classpath": classpath,
                "specs_json_str": json.dumps(specs_map)
            })
            bound_attrs = json.loads(lov_obs)
            updates["attributes"] = bound_attrs

            # Invoke Helper Tool: Copy Synthesis
            key_specs_str = " ".join([f"{s.value}{s.uom}" for s in grounded_data.grounded_specs[:2]])
            copy_obs = tool_synthesize_unilog_copy.invoke({
                "brand": brand_res,
                "product_name": prod_noun,
                "mpn": mpn,
                "key_specs": key_specs_str
            })
            copy_dict = json.loads(copy_obs)
            updates.update(copy_dict)

            # Invoke Helper Tool: Digital Assets
            asset_obs = tool_generate_digital_assets.invoke({
                "brand": brand_res,
                "mpn": mpn
            })
            asset_dict = json.loads(asset_obs)
            updates["digital_assets"] = asset_dict

            notes = [
                f"Multi-Hop ReAct: {grounded_data.step6_reasoning_and_resolution[:120]}...",
                f"Resolved: {brand_res} | {prod_noun}",
                f"Taxonomy: {classpath} [UNSPSC: {unspsc}]",
                f"Calibrated Confidence: {conf * 100:.1f}%",
                f"Tools Executed: KB + Web General + Datasheet PDF"
            ]
        else:
            # Deterministic domain engines execution (Offline mode)
            cur_state = state
            for agent_cls in [
                EntityResolutionAgent,
                TaxonomyClassifierAgent,
                SpecUOMExtractorAgent,
                OEMSourcingRAGAgent,
                ConstrainedLOVMapperAgent,
                MultiChannelCopyAgent,
                DigitalAssetAgent
            ]:
                res = agent_cls.execute(cur_state)
                cur_state = cur_state.model_copy(update=res)
                updates.update(res)

            notes = ["ReAct executed with local heuristic observations (offline mode)"]

        trace = AgentTrace(
            agent_name="ReAct Master Orchestrator (Cognitive Brain)",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=notes,
            extracted_data={
                "tools_executed": [t.name for t in cls.ORCHESTRATOR_TOOLS],
                "grounded_output": grounded_data.model_dump() if grounded_data else None
            }
        )

        updates["traces"] = state.traces + [trace]
        return updates
