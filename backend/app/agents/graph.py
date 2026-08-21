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
import logging

logger = logging.getLogger("OmniSpecAgentSwarm")


def node_agent_1(state: ProductEnrichmentState):
    logger.info("  [Agent 1/9: Ingestion & De-Noising] Starting tokenization & noise cleansing...")
    t0 = time.perf_counter()
    res = IngestionAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 1 ✓] Ingestion Complete ({ms} ms) — MPN: '{res.get('clean_mfg_part_num', '')}'")
    return res

def node_agent_2(state: ProductEnrichmentState):
    logger.info("  [Agent 2/9: Brand & Entity Resolution] Resolving OEM Brand & Trademark marks...")
    t0 = time.perf_counter()
    res = EntityResolutionAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 2 ✓] Brand Resolved: '{res.get('brand_name', '')}' ({res.get('manufacturer_name', '')}) ({ms} ms)")
    return res

def node_agent_3(state: ProductEnrichmentState):
    logger.info("  [Agent 3/9: Dynamic Taxonomy & UNSPSC] Classifying 4-tier category path...")
    t0 = time.perf_counter()
    res = TaxonomyClassifierAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 3 ✓] Taxonomy Assigned: '{res.get('classpath', '')}' [UNSPSC: {res.get('unspsc', '')}] ({ms} ms)")
    return res

def node_agent_4(state: ProductEnrichmentState):
    logger.info("  [Agent 4/9: Spec, Dimension & UOM Extractor] Parsing numerical dimensions & electrical/physical specs...")
    t0 = time.perf_counter()
    res = SpecUOMExtractorAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 4 ✓] Specs Extracted ({ms} ms)")
    return res

def node_agent_5(state: ProductEnrichmentState):
    logger.info("  [Agent 5/9: OEM Sourcing & CRAG] Crawling official technical PDF datasheets & web grounding...")
    t0 = time.perf_counter()
    res = OEMSourcingRAGAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 5 ✓] OEM Sourcing URL Grounded: '{res.get('mfr_url', '')}' ({ms} ms)")
    return res

def node_agent_6(state: ProductEnrichmentState):
    logger.info("  [Agent 6/9: Constrained LOV Mapper] Mapping attribute triples to 150-column Unilog schema...")
    t0 = time.perf_counter()
    res = ConstrainedLOVMapperAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 6 ✓] LOV Schema Attributes Bound ({ms} ms)")
    return res

def node_agent_7(state: ProductEnrichmentState):
    logger.info("  [Agent 7/9: Multi-Channel Copy Builder] Synthesizing strict character-bounded copy tiers...")
    t0 = time.perf_counter()
    res = MultiChannelCopyAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 7 ✓] Copy Synthesized ({ms} ms) — INVOICE: '{res.get('invoice_desc', '')}' ({len(res.get('invoice_desc', ''))}/40 chars)")
    return res

def node_agent_8(state: ProductEnrichmentState):
    logger.info("  [Agent 8/9: Digital Asset Synthesizer] Formatting standardized image and spec sheet names...")
    t0 = time.perf_counter()
    res = DigitalAssetAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 8 ✓] Digital Assets Generated: '{res.get('digital_assets', {}).get('Product Image', '')}' ({ms} ms)")
    return res

def node_agent_9(state: ProductEnrichmentState):
    logger.info("  [Agent 9/9: Quality Audit & HITL Orchestrator] Running 5-pillar evidence audit & lineage verification...")
    t0 = time.perf_counter()
    res = QualityAuditAgent.execute(state)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"  [Agent 9 ✓] Quality Audit Complete ({ms} ms) — Confidence: {res.get('overall_confidence', 0)*100:.1f}%, HITL: {res.get('needs_hitl_review')}")
    return res


def create_omnispec_graph():
    """
    Constructs and compiles the 9-Agent LangGraph Swarm DAG.
    Ingestion -> Entity Resolution -> Taxonomy -> Spec/UOM -> OEM Sourcing/CRAG -> LOV Mapper -> Copy Builder -> Digital Assets -> Quality Audit
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
    workflow.add_node("agent_9_quality_audit", node_agent_9)

    workflow.set_entry_point("agent_1_ingestion")
    workflow.add_edge("agent_1_ingestion", "agent_2_entity_resolution")
    workflow.add_edge("agent_2_entity_resolution", "agent_3_taxonomy")
    workflow.add_edge("agent_3_taxonomy", "agent_4_spec_uom")
    workflow.add_edge("agent_4_spec_uom", "agent_5_oem_sourcing")
    workflow.add_edge("agent_5_oem_sourcing", "agent_6_lov_mapper")
    workflow.add_edge("agent_6_lov_mapper", "agent_7_copy_builder")
    workflow.add_edge("agent_7_copy_builder", "agent_8_digital_assets")
    workflow.add_edge("agent_8_digital_assets", "agent_9_quality_audit")
    workflow.add_edge("agent_9_quality_audit", END)

    return workflow.compile()
