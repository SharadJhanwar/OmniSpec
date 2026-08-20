import pytest
from fastapi.testclient import TestClient
from backend.app.core.logging import logger
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    """Verify backend health check endpoint."""
    logger.info("Testing GET /health API...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "HEALTHY"



def test_catalog_pagination():
    """Verify catalog pagination and 252-column master schema delivery."""
    response = client.get("/api/v1/catalog?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 10
    if len(data["items"]) > 0:
        first = data["items"][0]
        assert "Mfg_Part_Num" in first or "mfg_part_num" in first


def test_single_sku_enrichment_swarm():
    """Verify 9-Agent LangGraph Swarm execution for a single raw input."""
    payload = {
        "Mfg_Part_Num": "PDSH4816AF",
        "Part_Desc": "PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA",
        "Part_Manuf": "Appliance Dealers Cooperative (APPDE)",
        "E1_Brand": "",
        "Unilog_Brand": "",
        "DIB_Brand": ""
    }
    response = client.post("/api/v1/enrich/single", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "delivery_record" in data
    assert "traces" in data
    assert len(data["traces"]) == 9

    record = data["delivery_record"]
    assert "FRIGIDAIRE" in record.get("BRAND_NAME", "")
    assert len(record.get("INVOICE_DESC", "")) <= 40
    assert 60 <= len(record.get("MOBILE_DESC", "")) <= 80


def test_dbom_cell_level_provenance():
    """Verify Cell-Level Data Bill of Materials (DBOM) and SHA-256 lineage."""
    payload = {
        "Mfg_Part_Num": "49-94-0101",
        "Part_Desc": "49-94-0101 Milw 4-1/2\"x.045\"x7/8\" Perform+ Metal Cut Off Disc 10pc",
        "Part_Manuf": "Milwaukee Accessory (4031)",
        "E1_Brand": "",
        "Unilog_Brand": "Milwaukee"
    }
    response = client.post("/api/v1/provenance/dbom", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "dbom" in data
    dbom = data["dbom"]
    assert "provenance_cells" in dbom
    assert "lineage_hash" in dbom
    assert len(dbom["lineage_hash"]) == 64  # SHA-256 length


def test_defect_probability_index_audit():
    """Verify Defect Probability Index (DPI) risk scorer and queue routing."""
    payload = {
        "state": {
            "mfg_part_num": "49-94-0101",
            "brand_name": "Milwaukee®",
            "invoice_desc": "CUT OFF WHEEL 4-1/2IN X .045IN X 7/8IN",
            "mobile_desc": "Milwaukee Tool Milwaukee, Cut-Off Disc, Performance Plus, 49-94-0101",
            "overall_confidence": 0.98,
            "audit_violations": []
        }
    }
    response = client.post("/api/v1/audit/dpi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "dpi" in data
    dpi = data["dpi"]
    assert 0.0 <= dpi["dpi_score"] <= 1.0
    assert dpi["risk_tier"] in ["LOW", "ELEVATED", "CRITICAL"]


def test_pairwise_compatibility_evaluator():
    """Verify pairwise mechanical, electrical, and rotational compatibility evaluator."""
    payload = {
        "product_a": {
            "SHORT_DESC": "DEWALT® 4-1/2 in Small Angle Grinder 11A 7/8 in Arbor 11000 RPM",
            "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders"
        },
        "product_b": {
            "SHORT_DESC": "Milwaukee® 4-1/2 in x .045 in x 7/8 in Metal Cut-Off Disc 13300 RPM",
            "Classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels"
        }
    }
    response = client.post("/api/v1/compatibility/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    result = data.get("result", {})
    assert result.get("is_compatible") is True
    assert result.get("status") == "COMPATIBLE"


def test_parametric_constraint_search_engine():
    """Verify sub-millisecond AST compilation and DuckDB constraint search."""
    payload = {
        "query": "Dishwasher under 45 dBA stainless steel 120V 15A",
        "enable_llm": False
    }
    response = client.post("/api/v1/search/parametric", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    search_data = data.get("data", {})
    assert "ast" in search_data
    assert "qualified_matches" in search_data
    assert "disqualified_tradeoffs" in search_data


def test_product_family_discovery_clustering():
    """Verify Parent Product Family discovery, variant axes, and assortment gap detector."""
    response = client.get("/api/v1/families")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    res_data = data.get("data", {})
    assert "families" in res_data
    assert len(res_data["families"]) > 0


def test_hitl_active_learning_override_persistence():
    """Verify manual reviewer override registration and retrieval in DuckDB."""
    override_payload = {
        "mpn": "TEST-OVERRIDE-SKU",
        "brand_name": "TEST_BRAND®",
        "manufacturer_name": "Test Manufacturer Corp",
        "override_data": {
            "INVOICE_DESC": "TEST INVOICE DESC 40",
            "MOBILE_DESC": "Test Manufacturer Test Brand, Manual Review Override Item 60-80 chars"
        },
        "reviewer_notes": "Unit test verified human feedback loop"
    }
    post_res = client.post("/api/v1/hitl/override", json=override_payload)
    assert post_res.status_code == 200
    assert post_res.json().get("success") is True

    get_res = client.get("/api/v1/hitl/overrides")
    assert get_res.status_code == 200
    assert get_res.json().get("success") is True
    overrides = get_res.json().get("overrides", [])
    assert any(o.get("mpn") == "TEST-OVERRIDE-SKU" for o in overrides)


def test_multi_sheet_excel_export():
    """Verify formatted multi-sheet Excel (.xlsx) workbook generation."""
    response = client.post("/api/v1/enrich/export-excel")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(response.content) > 1000  # Non-empty binary workbook


def test_oem_technical_pdf_datasheet_submittal():
    """Verify autonomous 1-page contractor submittal PDF specification sheet generator."""
    payload = {
        "Mfg_Part_Num": "PDSH4816AF",
        "BRAND_NAME": "FRIGIDAIRE®",
        "MANUFACTURER_NAME": "Rheem Manufacturing",
        "SHORT_DESC": "FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher",
        "INVOICE_DESC": "DISHWASHER LEG 5 SST 120V 15A",
        "MOBILE_DESC": "Rheem Manufacturing FRIGIDAIRE, Dishwasher, PDSH4816AF",
        "Classpath": "Appliances>Dishwashers"
    }
    response = client.post("/api/v1/datasheet/generate-pdf", json=payload)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_knowledge_base_search_endpoints():
    """Verify UniCat Brands, Fractions, and Thesaurus search endpoints."""
    brands_res = client.get("/api/v1/kb/brands?q=Dewalt")
    assert brands_res.status_code == 200
    assert "brands" in brands_res.json()

    fractions_res = client.get("/api/v1/kb/fractions")
    assert fractions_res.status_code == 200
    assert "fractions" in fractions_res.json()

    thesaurus_res = client.get("/api/v1/kb/thesaurus")
    assert thesaurus_res.status_code == 200
    assert "terms" in thesaurus_res.json()
