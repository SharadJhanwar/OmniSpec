import pytest
import logging
from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.graph import create_omnispec_graph
from backend.app.db.duckdb_client import kb

logger = logging.getLogger(__name__)


def test_hitl_active_learning_cycle():
    """
    Verifies the Complete HITL Active Learning Feedback Loop:
    1. An unseen ambiguous supplier is processed -> Low confidence / routes to HITL.
    2. Human specialist inspects and submits verified approval into DuckDB override store.
    3. The same product is re-processed -> Resolves instantly from KB with 100% confidence!
    """
    graph = create_omnispec_graph()
    test_mpn = "NOVEL-PUMP-99"

    # Step 1: Initial Processing of completely unseen supplier
    initial_state_1 = ProductEnrichmentState(
        row_id="hitl_cycle_1",
        raw_mfg_part_num=test_mpn,
        raw_part_desc="NOVEL-PUMP-99 Industrial Rotary Pump 2HP 230V 50 GPM",
        raw_e1_brand="-- Unbranded --",
        raw_unilog_brand="-- No Unilog Brand --",
        raw_dib_brand="-- No DIB Brand --",
        raw_part_manuf="Unknown Supply Distributor (UNKSUP)",
        enable_llm=False
    )

    state_1 = graph.invoke(initial_state_1)

    logger.info(f"Run 1 Resolved Brand: {state_1['brand_name']} | Confidence: {state_1['overall_confidence']}")
    # Verify initial run is uncached -> Needs HITL review
    assert state_1["needs_hitl_review"] is True, "Initial uncached SKU must trigger HITL review"

    # Step 2: Human Specialist approves and persists verified canonical knowledge into DuckDB
    kb.save_override(
        mpn=test_mpn,
        brand_name="Gorman-Rupp®",
        manufacturer_name="The Gorman-Rupp Company",
        override_data={"dept": "Plumbing", "class_name": "Pumps"},
        notes="Verified against Gorman-Rupp master pump catalog by Senior Data Specialist"
    )

    # Step 3: Second Processing of the exact same product
    initial_state_2 = ProductEnrichmentState(
        row_id="hitl_cycle_2",
        raw_mfg_part_num=test_mpn,
        raw_part_desc="NOVEL-PUMP-99 Industrial Rotary Pump 2HP 230V 50 GPM",
        raw_e1_brand="-- Unbranded --",
        raw_unilog_brand="-- No Unilog Brand --",
        raw_dib_brand="-- No DIB Brand --",
        raw_part_manuf="Unknown Supply Distributor (UNKSUP)",
        enable_llm=False
    )

    state_2 = graph.invoke(initial_state_2)

    logger.info(f"Run 2 Resolved Brand: {state_2['brand_name']} | Confidence: {state_2['overall_confidence']}")
    assert state_2["brand_name"] == "Gorman-Rupp®", "Must resolve to human-approved canonical brand"
    assert state_2["manufacturer_name"] == "The Gorman-Rupp Company", "Must resolve to human-approved manufacturer"
    assert state_2["overall_confidence"] == 1.0, "Approved knowledge must resolve with 100% confidence"
    assert state_2["needs_hitl_review"] is False, "Cached approved record must not require HITL"

    logger.info("HITL Active Learning feedback loop successfully verified with DuckDB persistence.")
