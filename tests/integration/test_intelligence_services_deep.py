import pytest
from backend.app.core.logging import logger
from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.services.parametric_search_engine import ParametricSearchEngine
from backend.app.services.compatibility_engine import CompatibilityEngine
from backend.app.services.family_clustering_engine import FamilyClusteringEngine
from backend.app.services.dbom_service import DBOMService
from backend.app.services.defect_risk_scorer import DefectRiskScorer

def test_ast_compiler_edge_cases():
    """Verify parametric search compiler across various industrial queries."""
    logger.info("Executing deep AST compiler edge cases test...")
    ast1 = ParametricSearchEngine.compile_query_to_ast("Dishwasher under 45 dBA stainless steel 120V 15A")
    assert ast1.category_intent is not None
    assert len(ast1.numerical_constraints) >= 1
    assert any(c.field == "Sound Level" and c.value == 45.0 for c in ast1.numerical_constraints)

    ast2 = ParametricSearchEngine.compile_query_to_ast("4-1/2 in cut off disc 7/8 in arbor over 10000 RPM")
    assert any(c.field == "Max RPM" and c.value == 10000.0 for c in ast2.numerical_constraints)


def test_compatibility_engine_mechanisms():
    """Verify pairwise mechanical, electrical, and physical compatibility logic."""
    logger.info("Executing deep compatibility engine mechanisms test...")
    # Test 1: Compatible Grinder & Wheel (Arbor match)
    tool = {"SHORT_DESC": "DEWALT 4-1/2 in Angle Grinder 11A 7/8 in arbor 11000 RPM", "Classpath": "Grinders"}
    wheel = {"SHORT_DESC": "Milwaukee 4-1/2 in x 7/8 in Cut-Off Disc", "Classpath": "Cut-Off Wheels"}
    res1 = CompatibilityEngine.evaluate_compatibility(tool, wheel)
    assert res1.is_compatible is True
    assert res1.status == "COMPATIBLE"

    # Test 2: Incompatible Arbor
    wheel_bad_arbor = {"SHORT_DESC": "Diablo 4-1/2 in x 5/8 in Cut-Off Disc", "Classpath": "Cut-Off Wheels"}
    res2 = CompatibilityEngine.evaluate_compatibility(tool, wheel_bad_arbor)
    assert res2.is_compatible is False
    assert res2.status == "INCOMPATIBLE"
    assert any("Arbor" in c for c in res2.conflict_specs)


def test_family_clustering_and_fractional_gaps():
    """Verify MPN decomposition, multi-axis variant induction, and fractional gap detector."""
    sample_skus = [
        {"Mfg_Part_Num": "CPLG-14-BRS", "BRAND_NAME": "Mueller Industries®", "SHORT_DESC": "1/4 in Brass Coupling 150# NPT", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings"},
        {"Mfg_Part_Num": "CPLG-38-BRS", "BRAND_NAME": "Mueller Industries®", "SHORT_DESC": "3/8 in Brass Coupling 150# NPT", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings"},
        {"Mfg_Part_Num": "CPLG-34-BRS", "BRAND_NAME": "Mueller Industries®", "SHORT_DESC": "3/4 in Brass Coupling 150# NPT", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings"}
    ]
    discovery_res = FamilyClusteringEngine.discover_product_families(sample_skus)
    assert len(discovery_res.families) == 1
    fam = discovery_res.families[0]
    assert fam.base_series_mpn == "CPLG-BRS"
    assert len(fam.variants) == 3
    assert len(fam.detected_gaps) == 1
    assert "1/2 in" in fam.detected_gaps[0].missing_sizes
    assert fam.detected_gaps[0].confidence_level == "CONFIRMED_MANUFACTURER_GAP"


def test_dbom_cryptographic_lineage_mutation():
    """Verify that any modification to an attribute changes the SHA-256 lineage hash."""
    state1 = ProductEnrichmentState(
        raw_mfg_part_num="PDSH4816AF",
        raw_part_desc="PDSH4816AF Dishwasher SS 24 in 120V 15A 47dBA",
        manufacturer_name="Rheem Manufacturing",
        brand_name="FRIGIDAIRE®",
        overall_confidence=0.98
    )
    dbom1 = DBOMService.generate_dbom(state1)
    hash1 = dbom1.lineage_hash

    # Modify an attribute
    state2 = ProductEnrichmentState(
        raw_mfg_part_num="PDSH4816AF-MOD",
        raw_part_desc="PDSH4816AF Dishwasher SS 24 in 120V 15A 47dBA",
        manufacturer_name="Rheem Manufacturing",
        brand_name="FRIGIDAIRE®",
        overall_confidence=0.85
    )
    dbom2 = DBOMService.generate_dbom(state2)
    hash2 = dbom2.lineage_hash

    assert hash1 != hash2
    assert len(hash1) == 64
    assert len(hash2) == 64


def test_dpi_risk_scoring_bounds():
    """Verify Defect Probability Index bounds and severity classification."""
    # Clean verified item -> Low Risk
    clean_state = ProductEnrichmentState(
        raw_mfg_part_num="49-94-0101",
        mfr_part_number="49-94-0101",
        brand_name="Milwaukee®",
        brand_confidence=1.0,
        invoice_desc="CUT OFF WHEEL 4-1/2IN X .045IN",
        mobile_desc="Milwaukee Tool Milwaukee, Cut-Off Disc, Performance Plus, 49-94-0101",
        overall_confidence=0.98,
        audit_violations=[]
    )
    dpi_clean = DefectRiskScorer.evaluate_risk(clean_state)
    assert dpi_clean.risk_tier == "LOW"
    assert dpi_clean.dpi_score < 0.35

    # Flawed item -> Elevated/Critical Risk
    flawed_state = ProductEnrichmentState(
        raw_mfg_part_num="UNKNOWN",
        mfr_part_number="",
        brand_name="generic",
        brand_confidence=0.40,
        invoice_desc="WAY TOO LONG INVOICE DESCRIPTION EXCEEDING FORTY CHARACTERS STRICT LIMIT",
        mobile_desc="Short",
        overall_confidence=0.45,
        audit_violations=["BRAND_TRADEMARK_MISSING", "INVOICE_DESC_EXCEEDS_40"]
    )
    dpi_flawed = DefectRiskScorer.evaluate_risk(flawed_state)
    assert dpi_flawed.risk_tier in ["ELEVATED", "CRITICAL"]
    assert len(dpi_flawed.top_risk_factors) >= 2
