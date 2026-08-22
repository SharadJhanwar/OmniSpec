import pytest
import logging
from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.graph import create_omnispec_graph

logger = logging.getLogger(__name__)


class TestUnseenCatalogGeneralization:
    """
    20-Item Novel Out-of-Distribution Catalog Generalization Test Suite.
    Verifies that genuinely unseen products across unmapped categories,
    novel industrial manufacturers, and diverse specifications are
    accurately parsed, enriched, categorized, and formatted into 252-column
    Unilog delivery records without cross-brand hallucination or schema violation.
    """

    UNSEEN_PRODUCTS = [
        # 1. Bearings & Power Transmission
        {
            "mpn": "6205-2RS1",
            "desc": "6205-2RS1 Deep Groove Ball Bearing 25mm Bore 52mm OD 15mm Width Rubber Sealed",
            "manuf": "SKF USA Inc (SKFUS)",
            "expected_dept": "Power Transmission",
            "expected_prod_name": "Ball Bearing"
        },
        # 2. Electrician Hand Tools
        {
            "mpn": "11055",
            "desc": "11055 Klein-Kurve Wire Stripper / Cutter 10-18 AWG Solid 12-20 AWG Stranded",
            "manuf": "Klein Tools Inc (KLEIN)",
            "expected_dept": "Tools",
            "expected_prod_name": "Wire Stripper"
        },
        # 3. Electrical Power Distribution
        {
            "mpn": "BR120",
            "desc": "BR120 Single Pole Type BR Circuit Breaker 20A 120V 10 kAIC",
            "manuf": "Eaton Corporation (EATON)",
            "expected_dept": "Electrical",
            "expected_prod_name": "Circuit Breaker"
        },
        # 4. Adhesives & Chemical Sealants
        {
            "mpn": "24221",
            "desc": "Loctite 242 Medium Strength Blue Threadlocker 10 ml Bottle",
            "manuf": "Henkel Corporation (HENK)",
            "expected_dept": "Chemicals",
            "expected_prod_name": "Threadlocker"
        },
        # 5. Insulated Hand Tools
        {
            "mpn": "17-001",
            "desc": "17-001 1000V Insulated Slotted Screwdriver 1/4 in x 4 in Shank",
            "manuf": "Wiha Tools USA (WIHA)",
            "expected_dept": "Tools",
            "expected_prod_name": "Screwdriver"
        },
        # 6. Safety PPE & Eye Protection
        {
            "mpn": "SF400AF",
            "desc": "SecureFit 400 Protective Eyewear Clear Lens Anti-Fog Black/Green Frame",
            "manuf": "3M Personal Safety (3MPSD)",
            "expected_dept": "Safety",
            "expected_prod_name": "Safety Glasses"
        },
        # 7. Cutting Tools / Router Bits
        {
            "mpn": "53045",
            "desc": "53045 Solid Carbide Spiral Flush Trim Router Bit 1/2 in Shank 1/2 in Cut Dia",
            "manuf": "Amana Tool Corp (AMANA)",
            "expected_dept": "Tools",
            "expected_prod_name": "Router Bit"
        },
        # 8. Metalworking Hand Tools
        {
            "mpn": "2049",
            "desc": "2049 3-Piece Aviation Snips Set Left Right Straight Cut Cr-V Steel",
            "manuf": "IRWIN Tools (IRWIN)",
            "expected_dept": "Tools",
            "expected_prod_name": "Aviation Snips"
        },
        # 9. Hydraulics & Fluid Power
        {
            "mpn": "100-08",
            "desc": "100-08 Industrial Hydraulic Hose 1/2 in ID 2-Wire Braid 3500 PSI 50 ft Reel",
            "manuf": "Parker Hannifin Corp (PARKER)",
            "expected_dept": "Hydraulics",
            "expected_prod_name": "Hydraulic Hose"
        },
        # 10. Test & Measurement
        {
            "mpn": "30012",
            "desc": "30012 Digital Multimeter True RMS 600V AC/DC Auto-Ranging CAT III",
            "manuf": "Fluke Corporation (FLUKE)",
            "expected_dept": "Testing",
            "expected_prod_name": "Digital Multimeter"
        },
        # 11. Tool Storage
        {
            "mpn": "48-22-8426",
            "desc": "PACKOUT Rolling Tool Box 22 in W x 18.6 in D x 25.6 in H 250 lbs Capacity",
            "manuf": "Milwaukee Tool (4031)",
            "expected_dept": "Storage",
            "expected_prod_name": "Tool Box"
        },
        # 12. Plumbing Sump Pumps
        {
            "mpn": "02801",
            "desc": "02801 1-1/2 in Cast Iron Submersible Sump Pump 1/3 HP 115V 3000 GPM",
            "manuf": "Liberty Pumps Inc (LIBER)",
            "expected_dept": "Plumbing",
            "expected_prod_name": "Sump Pump"
        },
        # 13. Novel Dishwasher Brand (verifies NO Whirlpool hallucination)
        {
            "mpn": "SHX78B75UC",
            "desc": "800 Series 24 in Built-In Dishwasher Stainless Steel 42 dBA CrystalDry 120V",
            "manuf": "BSH Home Appliances (BOSCH)",
            "expected_dept": "Appliances",
            "expected_prod_name": "Dishwasher"
        },
        # 14. Measuring & Levels
        {
            "mpn": "DWHT43003",
            "desc": "9 in Heavy Duty Magnetic Cast Aluminum Torpedo Level 3 Vials",
            "manuf": "Stanley Black & Decker (2585)",
            "expected_dept": "Tools",
            "expected_prod_name": "Torpedo Level"
        },
        # 15. Clamping & Workholding
        {
            "mpn": "70001",
            "desc": "70001 Heavy Duty C-Clamp 4 in Jaw Opening 2-1/4 in Throat Depth Ductile Iron",
            "manuf": "Wilton Tool (WILTN)",
            "expected_dept": "Tools",
            "expected_prod_name": "C-Clamp"
        },
        # 16. Sockets & Mechanics Tools
        {
            "mpn": "8100-SC-2",
            "desc": "Zyklop 1/2 in Drive Speed Ratchet Set Metric 37-Piece with Textile Box",
            "manuf": "Wera Tools Inc (WERA)",
            "expected_dept": "Tools",
            "expected_prod_name": "Ratchet Socket Set"
        },
        # 17. Packaging & Tapes
        {
            "mpn": "40-001",
            "desc": "40-001 Premium Grade Duct Tape 2 in x 60 yd Silver 10 mil Waterproof",
            "manuf": "Shurtape Technologies (SHUR)",
            "expected_dept": "Packaging",
            "expected_prod_name": "Duct Tape"
        },
        # 18. Carbide Cutting Tools
        {
            "mpn": "2608628",
            "desc": "1/4 in Shank Carbide Tipped Chamfer Router Bit 45 Degree 1-1/4 in Diameter",
            "manuf": "Bosch Power Tools (BOSCH)",
            "expected_dept": "Tools",
            "expected_prod_name": "Router Bit"
        },
        # 19. Fasteners & Retaining Rings
        {
            "mpn": "5100-50",
            "desc": "5100-50 External Retaining Ring 1/2 in Shaft Dia Carbon Spring Steel 100/Pack",
            "manuf": "Rotor Clip Company (ROTOR)",
            "expected_dept": "Hardware",
            "expected_prod_name": "Retaining Ring"
        },
        # 20. Raw Materials & Sheet Metal
        {
            "mpn": "G90-12",
            "desc": "G90-12 Galvanized Steel Sheet 24 Gauge 12 in x 24 in Corrosion Resistant",
            "manuf": "Midwest Steel Supply (MIDST)",
            "expected_dept": "Materials",
            "expected_prod_name": "Sheet Metal"
        }
    ]

    @pytest.fixture(scope="class")
    def graph(self):
        return create_omnispec_graph()

    @pytest.mark.parametrize("item", UNSEEN_PRODUCTS)
    def test_unseen_product_pipeline_enrichment(self, graph, item):
        """Verify each novel product passes all 9 agents cleanly."""
        initial_state = ProductEnrichmentState(
            row_id="unseen_test",
            raw_mfg_part_num=item["mpn"],
            raw_part_desc=item["desc"],
            raw_e1_brand="-- Unbranded --",
            raw_unilog_brand="-- No Unilog Brand --",
            raw_dib_brand="-- No DIB Brand --",
            raw_part_manuf=item["manuf"],
            enable_llm=False
        )

        final_state = graph.invoke(initial_state)
        rec = final_state["delivery_record"]
        assert rec is not None, f"Delivery record was not created for MPN: {item['mpn']}"

        # 1. Taxonomy & Department Verification
        assert final_state["dept"] == item["expected_dept"], (
            f"Taxonomy mismatch for {item['mpn']}: got '{final_state['dept']}', expected '{item['expected_dept']}'"
        )
        assert final_state["product_name"] == item["expected_prod_name"], (
            f"Product name mismatch for {item['mpn']}: got '{final_state['product_name']}', expected '{item['expected_prod_name']}'"
        )

        # 2. Unilog Channel Copy Bounds Verification
        assert len(rec.invoice_desc) <= 40, f"Invoice desc exceeds 40 chars: '{rec.invoice_desc}' ({len(rec.invoice_desc)})"
        assert rec.invoice_desc.isupper(), f"Invoice desc must be UPPERCASE: '{rec.invoice_desc}'"
        assert 60 <= len(rec.mobile_desc) <= 80, f"Mobile desc out of 60-80 chars window: '{rec.mobile_desc}' ({len(rec.mobile_desc)})"
        assert len(rec.short_desc) > 5, "Short desc must not be empty"
        assert len(rec.long_desc1) > 10, "Long desc must not be empty"

        # 3. Digital Asset Naming Specification Compliance (<Brand>_<MPN>.<ext> or Real URLs)
        assert rec.product_image.startswith("http") or rec.product_image.endswith((".jpg", ".png", ".webp")), f"Product image must be real URL or end with .jpg/.png/.webp: {rec.product_image}"
        assert rec.specification_sheet.endswith(".pdf"), f"Specification sheet must end with .pdf: {rec.specification_sheet}"
        if not rec.product_image.startswith("http"):
            assert "_" in rec.product_image, "Asset name must contain underscore separator"

        # 4. Agent Lineage Trace Verification (all 10 agents executed)
        assert len(final_state["traces"]) == 10, f"Expected 10 agent traces, got {len(final_state['traces'])}"

        logger.info(f"Unseen SKU {item['mpn']} enriched successfully: Dept={final_state['dept']}, Confidence={final_state['overall_confidence']}")

    def test_bosch_dishwasher_no_whirlpool_hallucination(self, graph):
        """
        Specialized validation: Bosch Dishwasher (SHX78B75UC) with 42 dBA
        must NOT hallucinate Whirlpool specs (41 dBA, Whirlpool 3rd Rack).
        """
        initial_state = ProductEnrichmentState(
            row_id="bosch_test",
            raw_mfg_part_num="SHX78B75UC",
            raw_part_desc="800 Series 24 in Built-In Dishwasher Stainless Steel 42 dBA CrystalDry 120V",
            raw_e1_brand="-- Unbranded --",
            raw_unilog_brand="-- No Unilog Brand --",
            raw_dib_brand="-- No DIB Brand --",
            raw_part_manuf="BSH Home Appliances (BOSCH)",
            enable_llm=False
        )

        final_state = graph.invoke(initial_state)
        rec = final_state["delivery_record"]

        # Check acoustic spec is correctly 42 dBA (from input), NOT 41 dBA (from Whirlpool)
        assert final_state["acoustic_specs"].get("Sound Level") == "42", "Acoustic level must be 42 dBA from description"

        # Check copy does NOT contain Whirlpool
        assert "WHIRLPOOL" not in rec.invoice_desc.upper()
        assert "WHIRLPOOL" not in rec.mobile_desc.upper()
        assert "WHIRLPOOL" not in rec.short_desc.upper()
        assert "WHIRLPOOL" not in rec.long_desc1.upper()

        logger.info("Bosch Dishwasher generalization test passed with zero brand cross-contamination.")
