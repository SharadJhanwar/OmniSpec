from langgraph.graph import StateGraph, END
from ..schemas.state_schema import ProductEnrichmentState
from .agent_1_ingestion import IngestionAgent
from .agent_2_entity_resolution import EntityResolutionAgent
from .agent_3_taxonomy import TaxonomyClassifierAgent
from .agent_4_spec_uom import SpecUOMExtractorAgent
from .agent_5_oem_sourcing import OEMSourcingRAGAgent
from .agent_6_lov_mapper import ConstrainedLOVMapperAgent
from .agent_7_copy_builder import MultiChannelCopyAgent
from .agent_8_digital_assets import DigitalAssetAgent
from .agent_9_quality_audit import QualityAuditAgent


import time
from ..core.logging import logger


def node_agent_1(state: ProductEnrichmentState):
    logger.info("  [Agent 1/10: Ingestion & De-Noising] ──► Calling Service: IngestionNormalizer & TokenizerEngine")
    t0 = time.perf_counter()
    res = IngestionAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 1/10 ✓] Ingestion Complete ({ms} ms) ── Clean MPN: '{res.get('clean_mfg_part_num', '')}', Clean Supplier: '{res.get('clean_supplier', '')}'")
    return res

def node_agent_2(state: ProductEnrichmentState):
    logger.info("  [Agent 2/10: UniCat Entity Resolution] ──► Calling Service: DuckDB.find_brand() & RapidFuzz Alias Engine")
    t0 = time.perf_counter()
    res = EntityResolutionAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 2/10 ✓] Brand Resolved ({ms} ms) ── Brand: '{res.get('brand_name', '')}', MFR: '{res.get('manufacturer_name', '')}'")
    return res

def node_agent_3(state: ProductEnrichmentState):
    logger.info("  [Agent 3/10: Dynamic Taxonomy & UNSPSC] ──► Calling Service: DuckDB.search_taxonomy() & 4-Tier Classpath Engine")
    t0 = time.perf_counter()
    res = TaxonomyClassifierAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 3/10 ✓] Taxonomy Assigned ({ms} ms) ── Classpath: '{res.get('classpath', '')}' [UNSPSC: {res.get('unspsc', '')}]")
    return res

def node_agent_4(state: ProductEnrichmentState):
    logger.info("  [Agent 4/10: Spec, Dim & UOM Parser] ──► Calling Service: FractionDecimalConverter & SpecDimensionExtractor")
    t0 = time.perf_counter()
    res = SpecUOMExtractorAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    dims_summary = ", ".join([f"{k}={v}" for k, v in res.get("dimensions", {}).items() if not k.endswith("_UOM")])
    logger.info(f"  [Agent 4/10 ✓] Specs & UOMs Extracted ({ms} ms) ── Dimensions: [{dims_summary}]")
    return res

def node_agent_5(state: ProductEnrichmentState):
    logger.info("  [Agent 5/10: OEM Sourcing & CRAG] ──► Calling Service: EvidenceDiscoveryService & DuckDuckGo OEM Search")
    t0 = time.perf_counter()
    res = OEMSourcingRAGAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 5/10 ✓] OEM Grounding Complete ({ms} ms) ── Official URL: '{res.get('mfr_url', '')}'")
    return res

def node_agent_6(state: ProductEnrichmentState):
    logger.info("  [Agent 6/10: Constrained LOV Mapper] ──► Calling Service: DuckDB.get_lov_schema() & CategorySchemaValidator")
    t0 = time.perf_counter()
    res = ConstrainedLOVMapperAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    attr_count = sum(1 for i in range(1, 51) if res.get("attributes", {}).get(f"ATTRIBUTE_VALUE {i}"))
    logger.info(f"  [Agent 6/10 ✓] LOV Schema Bound ({ms} ms) ── {attr_count} Validated Attribute Triples Mapped")
    return res

def node_agent_7(state: ProductEnrichmentState):
    logger.info("  [Agent 7/10: Multi-Channel Copy Builder] ──► Calling Service: CopySynthesisEngine & BoundedTextFormatter")
    t0 = time.perf_counter()
    res = MultiChannelCopyAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 7/10 ✓] 6-Tier Copy Synthesized ({ms} ms) ── INVOICE ({len(res.get('invoice_desc', ''))}/40): '{res.get('invoice_desc', '')}'")
    return res

def node_agent_8(state: ProductEnrichmentState):
    logger.info("  [Agent 8/10: Digital Asset Synthesizer] ──► Calling Service: CanonicalAssetNamingEngine & URLSynthesizer")
    t0 = time.perf_counter()
    res = DigitalAssetAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 8/10 ✓] Digital Assets Formatted ({ms} ms) ── Image: '{res.get('digital_assets', {}).get('Product Image', '')}'")
    return res

from ..orchestrator.attribute_finalizer_orchestrator import LangGraphReActAttributeFinalizer

def node_react_attribute_finalizer(state: ProductEnrichmentState):
    logger.info("  [Agent 9/10: ReAct Attribute Finalizer] ──► Calling Service: LangGraphReActSubGraph & DeepSpecMiner")
    t0 = time.perf_counter()
    res = LangGraphReActAttributeFinalizer.execute_react_loop(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    total_attrs = sum(1 for i in range(1, 51) if res.get("attributes", {}).get(f"ATTRIBUTE_VALUE {i}"))
    logger.info(f"  [Agent 9/10 ✓] ReAct Finalization Done ({ms} ms) ── {total_attrs} Total Structured Triples with Precise UOMs")
    return res

def node_agent_9(state: ProductEnrichmentState):
    logger.info("  [Agent 10/10: Quality Audit & HITL] ──► Calling Service: QualityAuditEngine & 12-Rule Integrity Auditor")
    t0 = time.perf_counter()
    res = QualityAuditAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    conf = res.get('overall_confidence', 0) * 100
    hitl = res.get('needs_hitl_review', False)
    logger.info(f"  [Agent 10/10 ✓] Quality Audit Complete ({ms} ms) ── Confidence: {conf:.1f}%, HITL Required: {hitl}")
    return res


def create_omnispec_graph():
    """
    Constructs and compiles the 10-Node LangGraph Swarm DAG:
    Ingestion -> Entity Resolution -> Taxonomy -> Spec/UOM -> OEM Sourcing/CRAG -> LOV Mapper -> Copy Builder -> Digital Assets -> ReAct Attribute Finalizer -> Quality Audit
    """
    workflow = StateGraph(ProductEnrichmentState)

    workflow.add_node("agent_1_ingestion", node_agent_1)
    workflow.add_node("agent_2_entity_resolution", node_agent_2)
    workflow.add_node("agent_3_taxonomy", node_agent_3)
    workflow.add_node("agent_4_spec_uom", node_agent_4)
    workflow.add_node("agent_5_oem_sourcing", node_agent_5)
    workflow.add_node("agent_6_lov_mapper", node_agent_6)
    workflow.add_node("agent_7_copy_builder", node_agent_7)
    workflow.add_node("agent_8_digital_assets", node_agent_8)
    workflow.add_node("react_attribute_finalizer", node_react_attribute_finalizer)
    workflow.add_node("agent_9_quality_audit", node_agent_9)

    workflow.set_entry_point("agent_1_ingestion")
    workflow.add_edge("agent_1_ingestion", "agent_2_entity_resolution")
    workflow.add_edge("agent_2_entity_resolution", "agent_3_taxonomy")
    workflow.add_edge("agent_3_taxonomy", "agent_4_spec_uom")
    workflow.add_edge("agent_4_spec_uom", "agent_5_oem_sourcing")
    workflow.add_edge("agent_5_oem_sourcing", "agent_6_lov_mapper")
    workflow.add_edge("agent_6_lov_mapper", "agent_7_copy_builder")
    workflow.add_edge("agent_7_copy_builder", "agent_8_digital_assets")
    workflow.add_edge("agent_8_digital_assets", "react_attribute_finalizer")
    workflow.add_edge("react_attribute_finalizer", "agent_9_quality_audit")
    workflow.add_edge("agent_9_quality_audit", END)

    return workflow.compile()
