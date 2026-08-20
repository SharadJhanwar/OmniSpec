import pytest
from backend.app.core.logging import logger
from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.agent_1_ingestion import IngestionAgent
from backend.app.agents.agent_2_entity_resolution import EntityResolutionAgent
from backend.app.agents.agent_3_taxonomy import TaxonomyClassifierAgent
from backend.app.agents.agent_4_spec_uom import SpecUOMExtractorAgent
from backend.app.agents.agent_6_lov_mapper import ConstrainedLOVMapperAgent

def test_taxonomy_4_tier_classpath_standard():
    """Verify that Agent 3 assigns valid 4-tier category paths with proper > delimiters."""
    logger.info("Testing Agent 3 taxonomy 4-tier hierarchy standards...")
    
    samples = [
        ("PDSH4816AF Built-In Dishwasher SS 24 in", "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers"),
        ("4-1/2 in Cut-Off Wheel Metal 7/8 Arbor", "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels"),
        ("3/8 in Brass Pipe Coupling 150# NPT", "Plumbing>Pipe, Tube & Hose Fittings>Pipe Fittings"),
        ("LED A19 60W Equivalent Light Bulb 2700K", "Lighting & Electrical>Light Bulbs & Lamps>LED Light Bulbs"),
        ("20V MAX Cordless Sliding Miter Saw", "Tools & Instruments>Power Tools>Saws & Blades>Circular & Miter Saws"),
        ("Enhance Basics Composite Decking Board 16 ft", "Building Materials>Decking & Railing>Decking Boards")
    ]
    
    for raw_desc, expected_path in samples:
        state = ProductEnrichmentState(
            raw_mfg_part_num="TEST-SKU",
            raw_part_desc=raw_desc
        )
        state = state.model_copy(update=IngestionAgent.execute(state))
        state = state.model_copy(update=TaxonomyClassifierAgent.execute(state))
        assert state.classpath == expected_path, f"Expected {expected_path}, got {state.classpath}"
        assert state.classpath.count(">") >= 2
        assert len(state.unspsc) == 8


def test_lov_attribute_triple_formatting():
    """Verify that Agent 6 constructs compliant (Label, Value, UOM) triples adhering to controlled LOVs."""
    logger.info("Testing Agent 6 150-column attribute triples mapping...")
    
    state = ProductEnrichmentState(
        raw_mfg_part_num="PDSH4816AF",
        raw_part_desc="PDSH4816AF Dishwasher SS 24 in W x 24.25 in D 120V 15A 47dBA",
        brand_name="FRIGIDAIRE®",
        manufacturer_name="Rheem Manufacturing"
    )
    
    # Run full sequence
    state = state.model_copy(update=IngestionAgent.execute(state))
    state = state.model_copy(update=TaxonomyClassifierAgent.execute(state))
    state = state.model_copy(update=SpecUOMExtractorAgent.execute(state))
    state = state.model_copy(update=ConstrainedLOVMapperAgent.execute(state))
    
    attrs = state.attributes
    assert isinstance(attrs, dict)
    assert attrs.get("ATTRIBUTE_LABEL 1") != ""
    assert attrs.get("ATTRIBUTE_VALUE 1") != ""
    
    # Check that at least 3 attributes are populated
    populated_labels = [v for k, v in attrs.items() if k.startswith("ATTRIBUTE_LABEL") and v]
    assert len(populated_labels) >= 3
