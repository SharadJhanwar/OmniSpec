import pytest
from backend.app.core.logging import logger
from backend.app.services.family_clustering_engine import FamilyClusteringEngine
from backend.app.schemas.family_schema import ParentProductFamily, FamilyDiscoveryResponse


def test_task25_mpn_decomposition():
    """
    Test Task 25: Deterministic MPN decomposition across power tools, appliances, and fittings.
    """
    logger.info("Executing Task 25: MPN Decomposition & Variant Suffix Parser Test...")
    # 1. Power Tool Kit Suffixes
    base_1, axes_1 = FamilyClusteringEngine.decompose_mpn("DCG413B")
    assert base_1 == "DCG413"
    assert axes_1["Configuration"] == "Bare Tool (Tool Only)"

    base_2, axes_2 = FamilyClusteringEngine.decompose_mpn("DCG413P2")
    assert base_2 == "DCG413"
    assert "2-Battery Kit" in axes_2["Configuration"]

    # 2. Bosch Dishwasher Suffixes
    base_3, axes_3 = FamilyClusteringEngine.decompose_mpn("SHX78B75UC")
    assert base_3 == "SHX78B7"
    assert axes_3["Finish"] == "Stainless Steel"

    base_4, axes_4 = FamilyClusteringEngine.decompose_mpn("SHX78B76UC")
    assert base_4 == "SHX78B7"
    assert axes_4["Finish"] == "Black Stainless Steel"

    # 3. Fitting Series Suffixes
    base_5, axes_5 = FamilyClusteringEngine.decompose_mpn("CPLG-14-BRS")
    assert base_5 == "CPLG-BRS"
    assert axes_5["Nominal Pipe Size"] == "1/4 in"


def test_task25_family_discovery_clustering():
    """
    Test Task 25: Catalog-wide parent product family discovery and variant induction.
    """
    logger.info("Executing Task 25: Product Family Discovery & Variant Induction Test...")
    items = [
        {"Mfg_Part_Num": "DCG413B", "BRAND_NAME": "DEWALT®", "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders", "SHORT_DESC": "DEWALT® 20V MAX* XR 4-1/2 in Brushless Angle Grinder (Tool Only)"},
        {"Mfg_Part_Num": "DCG413P2", "BRAND_NAME": "DEWALT®", "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders", "SHORT_DESC": "DEWALT® 20V MAX* XR 4-1/2 in Brushless Angle Grinder Kit (2x 5.0Ah Batteries)"},
        {"Mfg_Part_Num": "SHX78B75UC", "BRAND_NAME": "Bosch®", "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "SHORT_DESC": "Bosch® 800 Series 24 in Built-In Dishwasher Stainless Steel 42 dBA"},
        {"Mfg_Part_Num": "SHX78B76UC", "BRAND_NAME": "Bosch®", "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "SHORT_DESC": "Bosch® 800 Series 24 in Built-In Dishwasher Black Stainless Steel 42 dBA"}
    ]

    resp = FamilyClusteringEngine.discover_product_families(items)

    assert resp.total_families_discovered == 2
    assert resp.total_child_skus_clustered == 4

    dewalt_fam = next(f for f in resp.families if "DCG413" in f.base_series_mpn)
    assert dewalt_fam.total_variants == 2
    assert any(ax.name == "Configuration" for ax in dewalt_fam.variant_axes)

    bosch_fam = next(f for f in resp.families if "SHX78B7" in f.base_series_mpn)
    assert bosch_fam.total_variants == 2
    assert any(ax.name == "Finish" for ax in bosch_fam.variant_axes)


def test_task26_assortment_gap_detection():
    """
    Test Task 26: Evidence-backed fractional dimensional sequence gap detection.
    """
    logger.info("Executing Task 26: Fractional Sequence Assortment Gap Detector Test...")
    items = [
        {"Mfg_Part_Num": "CPLG-14-BRS", "BRAND_NAME": "Mueller Industries®", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings", "SHORT_DESC": "Mueller® 1/4 in Brass Pipe Coupling 150# NPT Threaded"},
        {"Mfg_Part_Num": "CPLG-38-BRS", "BRAND_NAME": "Mueller Industries®", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings", "SHORT_DESC": "Mueller® 3/8 in Brass Pipe Coupling 150# NPT Threaded"},
        {"Mfg_Part_Num": "CPLG-34-BRS", "BRAND_NAME": "Mueller Industries®", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings", "SHORT_DESC": "Mueller® 3/4 in Brass Pipe Coupling 150# NPT Threaded"}
    ]

    resp = FamilyClusteringEngine.discover_product_families(items)

    assert len(resp.all_gaps) >= 1
    gap = resp.all_gaps[0]
    assert gap.dimension_name == "Nominal Pipe Size"
    assert "1/2 in" in gap.missing_sizes
    assert gap.gap_severity == "HIGH"
    assert gap.confidence_level == "CONFIRMED_MANUFACTURER_GAP"
    assert "1/4 in" in gap.present_sizes and "3/4 in" in gap.present_sizes
