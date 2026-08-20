import pytest
from backend.app.core.logging import logger
from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.graph import create_omnispec_graph
from backend.app.services.dbom_service import DBOMService
from backend.app.services.defect_risk_scorer import DefectRiskScorer
from backend.app.services.compatibility_engine import CompatibilityEngine


@pytest.fixture
def graph():
    return create_omnispec_graph()


def test_task19_cell_level_provenance_dbom(graph):
    """
    Test Task 19: Generates Data Bill of Materials (DBOM) with fine-grained lineage metadata.
    """
    logger.info("Executing Task 19: Cell-Level Provenance & DBOM Lineage Test...")
    initial_state = ProductEnrichmentState(
        row_id="test_dbom_1",
        raw_mfg_part_num="PDSH4816AF",
        raw_part_desc="PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA",
        raw_part_manuf="Appliance Dealers Cooperative (APPDE)"
    )

    final_state_dict = graph.invoke(initial_state)
    state = ProductEnrichmentState(**final_state_dict)

    dbom = DBOMService.generate_dbom(state=state, dpi_score=0.12, risk_tier="LOW")

    assert dbom.mpn == "PDSH4816AF"
    assert dbom.brand_name == "FRIGIDAIRE®"
    assert dbom.total_attributes_tracked >= 10
    assert dbom.lineage_hash != ""

    # Check specific cell provenances
    assert "BRAND_NAME" in dbom.provenance_cells
    assert dbom.provenance_cells["BRAND_NAME"].source_type == "UNICAT_BRAND_KB"
    assert dbom.provenance_cells["BRAND_NAME"].agent_name == "agent_2_entity_resolution"

    assert "INVOICE_DESC" in dbom.provenance_cells
    assert dbom.provenance_cells["INVOICE_DESC"].source_type == "FORMULA_DERIVED"
    assert "Length <= 40 Chars" in dbom.provenance_cells["INVOICE_DESC"].rule_applied

    assert "MFR URL" in dbom.provenance_cells
    assert dbom.provenance_cells["MFR URL"].source_type == "OEM_OFFICIAL_URL"


def test_task20_defect_probability_index():
    """
    Test Task 20: Evaluates Defect Probability Index (DPI) and risk tiers.
    """
    logger.info("Executing Task 20: Defect Probability Index (DPI) Risk Audit Test...")
    # Clean, valid state
    clean_state = ProductEnrichmentState(
        brand_name="Milwaukee®",
        brand_confidence=1.0,
        mfr_part_number="49-94-0101",
        invoice_desc="MILW 4-1/2X.045X7/8 CUTOFF 10PK",
        mobile_desc="Milwaukee Electric Tool Corporation Milwaukee, Cut-Off Disc, 49-94-0101",
        mfr_url="https://www.milwaukeetool.com/49-94-0101",
        sourcing_confidence=1.0
    )

    clean_risk = DefectRiskScorer.evaluate_risk(clean_state)
    assert clean_risk.dpi_score < 0.30
    assert clean_risk.risk_tier == "LOW"
    assert clean_risk.recommended_action == "AUTO_APPROVE"

    # Corrupted / High-risk state (invoice > 40 chars, missing brand symbol, low confidence)
    corrupt_state = ProductEnrichmentState(
        brand_name="Unknown Unbranded Brand",
        brand_confidence=0.40,
        mfr_part_number="UNKNOWN-MPN",
        invoice_desc="THIS IS AN EXTREMELY LONG INVOICE DESCRIPTION THAT EXCEEDS THE FORTY CHARACTER MAXIMUM CAP BY FAR",
        mobile_desc="Short",
        mfr_url="",
        sourcing_confidence=0.20
    )

    corrupt_risk = DefectRiskScorer.evaluate_risk(corrupt_state)
    assert corrupt_risk.dpi_score > 0.50
    assert corrupt_risk.risk_tier in ["ELEVATED", "CRITICAL"]
    assert corrupt_risk.recommended_action in ["SECONDARY_AUDIT", "IMMEDIATE_HITL_REQUIRED"]
    assert len(corrupt_risk.top_risk_factors) >= 2


def test_task21_compatibility_and_substitutes():
    """
    Test Task 21: Evaluates engineering compatibility and cross-brand substitutes.
    """
    logger.info("Executing Task 21: Pairwise Compatibility & Cross-Brand Substitutes Test...")
    # 1. Matching Arbor Compatibility
    tool_grinder = {"SHORT_DESC": "DEWALT® 4-1/2 in Small Angle Grinder 11A 7/8 in Arbor 11000 RPM"}
    disc_compatible = {"SHORT_DESC": "Milwaukee® 4-1/2 in x .045 in x 7/8 in Metal Cut-Off Disc"}
    disc_incompatible_arbor = {"SHORT_DESC": "Diablo® 4-1/2 in x .045 in x 5/8 in Metal Cut-Off Disc"}

    match_res = CompatibilityEngine.evaluate_compatibility(tool_grinder, disc_compatible)
    assert match_res.is_compatible is True
    assert match_res.status == "COMPATIBLE"
    assert any("7/8" in m for m in match_res.matched_specs)

    mismatch_res = CompatibilityEngine.evaluate_compatibility(tool_grinder, disc_incompatible_arbor)
    assert mismatch_res.is_compatible is False
    assert mismatch_res.status == "INCOMPATIBLE"
    assert len(mismatch_res.conflict_specs) > 0

    # 2. Voltage Compatibility
    drill_20v = {"SHORT_DESC": "DEWALT® 20V MAX* Cordless Compact Drill Bare Tool"}
    battery_20v = {"SHORT_DESC": "DEWALT® 20V MAX* 5.0Ah Lithium-Ion Battery Pack"}
    battery_12v = {"SHORT_DESC": "Milwaukee® M12 12V Compact Battery Pack"}

    volt_match = CompatibilityEngine.evaluate_compatibility(drill_20v, battery_20v)
    assert volt_match.is_compatible is True

    volt_mismatch = CompatibilityEngine.evaluate_compatibility(drill_20v, battery_12v)
    assert volt_mismatch.is_compatible is False

    # 3. Cross-Brand Substitutes
    substitutes = CompatibilityEngine.find_cross_brand_substitutes(
        mpn="49-94-0101",
        brand="Milwaukee®",
        desc="4-1/2 x .045 x 7/8 Cut Off Disc"
    )
    assert len(substitutes.substitutes) >= 2
    sub_brands = [s.substitute_brand for s in substitutes.substitutes]
    assert "Diablo®" in sub_brands or "3M™" in sub_brands or "DEWALT®" in sub_brands
