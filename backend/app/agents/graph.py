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


def node_agent_1(state: ProductEnrichmentState):
    return IngestionAgent.execute(state)

def node_agent_2(state: ProductEnrichmentState):
    return EntityResolutionAgent.execute(state)

def node_agent_3(state: ProductEnrichmentState):
    return TaxonomyClassifierAgent.execute(state)

def node_agent_4(state: ProductEnrichmentState):
    return SpecUOMExtractorAgent.execute(state)

def node_agent_5(state: ProductEnrichmentState):
    return OEMSourcingRAGAgent.execute(state)

def node_agent_6(state: ProductEnrichmentState):
    return ConstrainedLOVMapperAgent.execute(state)

def node_agent_7(state: ProductEnrichmentState):
    return MultiChannelCopyAgent.execute(state)

def node_agent_8(state: ProductEnrichmentState):
    return DigitalAssetAgent.execute(state)

def node_agent_9(state: ProductEnrichmentState):
    return QualityAuditAgent.execute(state)


def create_omnispec_graph():
    """
    Constructs and compiles the 9-Agent LangGraph Swarm DAG.
    Ingestion -> Entity Resolution -> Taxonomy -> Spec/UOM -> OEM Sourcing -> LOV Mapper -> Copy Builder -> Digital Assets -> Quality Audit
    """
    workflow = StateGraph(ProductEnrichmentState)

    # Register all 9 micro-agent nodes
    workflow.add_node("agent_1_ingestion", node_agent_1)
    workflow.add_node("agent_2_entity_resolution", node_agent_2)
    workflow.add_node("agent_3_taxonomy", node_agent_3)
    workflow.add_node("agent_4_spec_uom", node_agent_4)
    workflow.add_node("agent_5_oem_sourcing", node_agent_5)
    workflow.add_node("agent_6_lov_mapper", node_agent_6)
    workflow.add_node("agent_7_copy_builder", node_agent_7)
    workflow.add_node("agent_8_digital_assets", node_agent_8)
    workflow.add_node("agent_9_quality_audit", node_agent_9)

    # Define linear execution edges in DAG
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
