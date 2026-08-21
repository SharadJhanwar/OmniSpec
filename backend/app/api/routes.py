import csv
import io
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..schemas.state_schema import ProductEnrichmentState
from ..agents.graph import create_omnispec_graph
from ..schemas.delivery_schema import DeliveryProductRecord
from ..db.duckdb_client import kb
from ..services.excel_exporter import ExcelDeliveryExporter
from ..services.vision_spec_rag import VisionSpecSheetRAG
from ..services.pdf_datasheet_generator import PDFDatasheetGenerator
from ..services.dbom_service import DBOMService
from ..services.defect_risk_scorer import DefectRiskScorer
from ..services.compatibility_engine import CompatibilityEngine
from ..services.parametric_search_engine import ParametricSearchEngine
from ..services.family_clustering_engine import FamilyClusteringEngine


from ..core.logging import logger

router = APIRouter()
pipeline_graph = create_omnispec_graph()


class ReviewerOverridePayload(BaseModel):
    mpn: str
    brand_name: Optional[str] = ""
    manufacturer_name: Optional[str] = ""
    trade_name: Optional[str] = ""
    override_data: Optional[Dict[str, Any]] = None
    corrected_fields: Optional[Dict[str, Any]] = None
    reviewer_notes: Optional[str] = "Human reviewer manual validation"



@router.post("/enrich/single", response_model=Dict[str, Any])
async def enrich_single_item(item: Dict[str, Any]):
    """
    Enriches a single raw catalog row through the 9-Agent LangGraph Swarm.
    """
    mpn = item.get("Mfg_Part_Num", item.get("mfg_part_num", "")).strip()
    desc = item.get("Part_Desc", item.get("part_desc", "")).strip()

    logger.info("==================================================================================")
    logger.info(f"⚡ [REST API: /api/v1/enrich/single] Ingesting Single SKU")
    logger.info(f"   • MPN:  '{mpn}'")
    logger.info(f"   • Desc: '{desc}'")
    logger.info("----------------------------------------------------------------------------------")

    initial_state = ProductEnrichmentState(
        row_id=item.get("row_id", "row_1"),
        raw_mfg_part_num=mpn,
        raw_part_desc=desc,
        raw_e1_brand=item.get("E1_Brand", item.get("e1_brand", "")),
        raw_unilog_brand=item.get("Unilog_Brand", item.get("unilog_brand", "")),
        raw_dib_brand=item.get("DIB_Brand", item.get("dib_brand", "")),
        raw_part_manuf=item.get("Part_Manuf", item.get("part_manuf", "")),
        raw_sku=item.get("SKU", item.get("sku", "")),
        enable_llm=item.get("enable_llm", False)
    )

    final_state = pipeline_graph.invoke(initial_state)
    delivery_dict = final_state["delivery_record"].to_delivery_dict() if final_state.get("delivery_record") else {}

    logger.info(f"✓ [REST API: /api/v1/enrich/single] Enrichment Complete:")
    logger.info(f"   • Brand: '{final_state.get('brand_name')}' | Product: '{final_state.get('product_name')}'")
    logger.info(f"   • Confidence: {final_state.get('overall_confidence', 1.0)*100:.1f}% | HITL Required: {final_state.get('needs_hitl_review')}")
    logger.info("==================================================================================")

    return {
        "success": True,
        "overall_confidence": final_state.get("overall_confidence", 1.0),
        "needs_hitl_review": final_state.get("needs_hitl_review", False),
        "violations": final_state.get("integrity_violations", []),
        "traces": [t.model_dump() for t in final_state.get("traces", [])],
        "delivery_record": delivery_dict
    }


def parse_catalog_feed(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Parses incoming feed files supporting CSV, Excel (.xlsx, .xls), and JSON.
    """
    fn = filename.lower()
    if fn.endswith(".csv"):
        reader = csv.reader(io.StringIO(content.decode("utf-8", errors="ignore")))
        all_csv_rows = [row for row in reader if any(str(c).strip() for c in row)]
        if not all_csv_rows:
            return []
        first_row = [str(c).strip() for c in all_csv_rows[0]]
        exact_headers = {"mfg_part_num", "part_desc", "part_number", "sku", "mpn", "e1_brand", "unilog_brand", "dib_brand", "part_manuf"}
        has_headers = any(c.lower() in exact_headers for c in first_row)
        is_data_first = any(c.startswith("--") or bool(re.search(r"^\d+[A-Za-z0-9_-]+", c)) for c in first_row)
        
        pos_cols = ["Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf", "SKU"]
        if is_data_first or not has_headers:
            parsed_rows = []
            for r in all_csv_rows:
                r_dict = {pos_cols[i]: r[i].strip() for i in range(min(len(r), len(pos_cols)))}
                parsed_rows.append(r_dict)
            return parsed_rows
        else:
            headers = first_row
            parsed_rows = []
            for r in all_csv_rows[1:]:
                r_dict = {headers[i]: r[i].strip() for i in range(min(len(r), len(headers)))}
                parsed_rows.append(r_dict)
            return parsed_rows

    elif fn.endswith((".xlsx", ".xls")):
        import pandas as pd
        df = pd.read_excel(io.BytesIO(content))
        raw_cols = [str(c).strip() for c in df.columns]
        is_data_header = any(
            c.startswith("--") or 
            bool(re.search(r"^\d+[A-Za-z0-9_-]+", c)) or 
            "inc" in c.lower() or 
            "llc" in c.lower() or 
            "abranet" in c.lower() or 
            "diablo" in c.lower() 
            for c in raw_cols
        )
        exact_headers = {"mfg_part_num", "part_desc", "part_number", "sku", "mpn", "e1_brand", "unilog_brand", "dib_brand", "part_manuf"}
        has_exact_headers = any(c.lower() in exact_headers for c in raw_cols)

        if (is_data_header or not has_exact_headers) and df.shape[1] >= 2:
            df_no_header = pd.read_excel(io.BytesIO(content), header=None)
            pos_cols = ["Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf", "SKU"]
            col_map = {i: pos_cols[i] for i in range(min(df_no_header.shape[1], len(pos_cols)))}
            df_no_header = df_no_header.rename(columns=col_map)
            df = df_no_header

        df = df.fillna("")
        return df.to_dict(orient="records")
    elif fn.endswith(".json"):
        import json
        data = json.loads(content.decode("utf-8", errors="ignore"))
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "records" in data:
            return data["records"]
        elif isinstance(data, dict):
            return [data]
        return []
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{filename}'. Supported formats: .csv, .xlsx, .xls, .json"
        )


@router.post("/enrich/batch")
async def enrich_batch_csv(file: UploadFile = File(...)):
    """
    Upload a raw feed (.csv, .xlsx, .json) and receive full 252-column enriched CSV.
    """
    content = await file.read()
    rows = parse_catalog_feed(content, file.filename)

    logger.info("==================================================================================")
    logger.info(f"⚡ [REST API: /api/v1/enrich/batch] Ingesting Catalog Feed '{file.filename}' ({len(rows)} rows)")
    logger.info("==================================================================================")

    enriched_records = []
    for idx, row in enumerate(rows):
        mpn = str(row.get("Mfg_Part_Num", row.get("mfg_part_num", ""))).strip()
        desc = str(row.get("Part_Desc", row.get("part_desc", ""))).strip()
        logger.info(f"[{idx+1}/{len(rows)}] ──► Processing MPN: '{mpn}', Desc: '{desc}'")

        initial_state = ProductEnrichmentState(
            row_id=f"row_{idx+1}",
            raw_mfg_part_num=mpn,
            raw_part_desc=desc,
            raw_e1_brand=str(row.get("E1_Brand", row.get("e1_brand", ""))),
            raw_unilog_brand=str(row.get("Unilog_Brand", row.get("unilog_brand", ""))),
            raw_dib_brand=str(row.get("DIB_Brand", row.get("dib_brand", ""))),
            raw_part_manuf=str(row.get("Part_Manuf", row.get("part_manuf", "")))
        )
        final_state = pipeline_graph.invoke(initial_state)
        if final_state.get("delivery_record"):
            enriched_records.append(final_state["delivery_record"].to_delivery_dict())

    if not enriched_records:
        raise HTTPException(status_code=400, detail="No valid records found in uploaded file.")

    logger.info(f"✓ [REST API: /api/v1/enrich/batch] Completed {len(enriched_records)} records.")

    output = io.StringIO()
    fieldnames = list(enriched_records[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(enriched_records)

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=OmniSpec_Enriched_Delivery_252.csv"}
    )


@router.post("/enrich/batch-json")
async def enrich_batch_csv_json(file: UploadFile = File(...)):
    """
    Upload a feed (.csv, .xlsx, .xls, .json) and receive an array of enriched 252-column JSON records.
    """
    content = await file.read()
    rows = parse_catalog_feed(content, file.filename)

    logger.info("==================================================================================")
    logger.info(f"⚡ [REST API: /api/v1/enrich/batch-json] Received Catalog Feed '{file.filename}' ({len(rows)} products)")
    logger.info("==================================================================================")

    enriched_records = []
    for idx, row in enumerate(rows):
        mpn = str(row.get("Mfg_Part_Num", row.get("mfg_part_num", ""))).strip()
        desc = str(row.get("Part_Desc", row.get("part_desc", ""))).strip()
        logger.info(f"\n[{idx+1}/{len(rows)}] ──► Starting 10-Agent Swarm Pipeline for MPN: '{mpn}' | Desc: '{desc}'")

        initial_state = ProductEnrichmentState(
            row_id=f"row_{idx+1}",
            raw_mfg_part_num=mpn,
            raw_part_desc=desc,
            raw_e1_brand=str(row.get("E1_Brand", row.get("e1_brand", ""))),
            raw_unilog_brand=str(row.get("Unilog_Brand", row.get("unilog_brand", ""))),
            raw_dib_brand=str(row.get("DIB_Brand", row.get("dib_brand", ""))),
            raw_part_manuf=str(row.get("Part_Manuf", row.get("part_manuf", "")))
        )
        final_state = pipeline_graph.invoke(initial_state)
        if final_state.get("delivery_record"):
            rec_dict = final_state["delivery_record"].to_delivery_dict()
            rec_dict["_confidence"] = final_state.get("overall_confidence", 1.0)
            rec_dict["_needs_hitl"] = final_state.get("needs_hitl_review", False)
            rec_dict["_traces"] = [t.model_dump() for t in final_state.get("traces", [])]
            enriched_records.append(rec_dict)

        logger.info(f"  ✓ [Item {idx+1}/{len(rows)} Complete] Resolved Brand='{final_state.get('brand_name')}', Conf={final_state.get('overall_confidence', 1.0)*100:.1f}%, HITL={final_state.get('needs_hitl_review')}")

    logger.info("==================================================================================")
    logger.info(f"✓ [REST API: /api/v1/enrich/batch-json] Batch Processing Finished: {len(enriched_records)}/{len(rows)} Enriched")
    logger.info("==================================================================================")

    return {
        "success": True,
        "count": len(enriched_records),
        "records": enriched_records
    }


@router.post("/enrich/export-excel")
async def export_excel_workbook(payload: Optional[Dict[str, Any]] = Body(None)):
    """
    Exports the enriched dataset (or currently uploaded batch) as a multi-sheet, styled .xlsx workbook.
    """
    import re
    filename = "OmniSpec_Delivery_Enriched_252.xlsx"
    records = []

    if payload and isinstance(payload.get("items"), list) and len(payload["items"]) > 0:
        records = payload["items"]
        if payload.get("filename"):
            clean_fn = re.sub(r"[^a-zA-Z0-9_-]", "_", Path(payload["filename"]).stem)
            filename = f"OmniSpec_Enriched_{clean_fn}_252.xlsx"
        else:
            filename = "OmniSpec_Current_Batch_Enriched_252.xlsx"
    else:
        csv_path = Path(__file__).resolve().parent.parent.parent.parent / "OmniSpec_Enriched_1000_Items_Delivery_252.csv"
        if csv_path.exists():
            with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                records = list(reader)
        elif len(SEED_CATALOG) > 0:
            records = SEED_CATALOG

    if not records:
        raise HTTPException(status_code=404, detail="No catalog records available for export.")

    excel_bytes = ExcelDeliveryExporter.export_delivery_workbook(records)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/datasheet/generate-pdf")
async def generate_datasheet_pdf(record: Dict[str, Any]):
    """
    Generates a 1-page engineering PDF specification cut sheet for an enriched item.
    """
    pdf_bytes = PDFDatasheetGenerator.generate_datasheet(record)
    mpn = record.get("Mfg_Part_Num", record.get("mfg_part_number", "SpecSheet")).replace("/", "_")
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={mpn}_Specification_Sheet.pdf"}
    )


@router.post("/hitl/override")
async def save_reviewer_override(payload: ReviewerOverridePayload):
    """
    Active Learning Feedback Loop: Saves manual human corrections into DuckDB
    so subsequent swarm executions automatically adopt the approved master entities.
    """
    override_dict = payload.override_data or payload.corrected_fields or {}
    if payload.trade_name:
        override_dict["trade_name"] = payload.trade_name

    kb.save_override(
        mpn=payload.mpn,
        brand_name=payload.brand_name,
        manufacturer_name=payload.manufacturer_name,
        override_data=override_dict,
        notes=payload.reviewer_notes or ""
    )
    return {
        "success": True,
        "message": f"Active learning override registered for MPN: {payload.mpn}",
        "mpn": payload.mpn
    }


@router.get("/hitl/overrides")
async def get_all_reviewer_overrides():
    """
    Returns all registered active learning human reviewer overrides.
    """
    overrides = kb.get_all_overrides()
    return {
        "success": True,
        "count": len(overrides),
        "overrides": overrides
    }


@router.post("/enrich/vision")
async def extract_from_vision_spec(file: UploadFile = File(...)):
    """
    Multimodal Vision RAG: Extracts structured dimensions and specs from uploaded drawing/image.
    """
    image_bytes = await file.read()
    mime = file.content_type or "image/jpeg"
    result = VisionSpecSheetRAG.extract_from_image_bytes(image_bytes, mime)
    return result


@router.get("/kb/stats")
async def get_kb_statistics():
    """
    Returns aggregate statistics across master knowledge tables.
    """
    return kb.get_kb_stats()


@router.get("/kb/brands")
async def search_kb_brands(q: str = ""):
    """
    Search canonical UniCat brands table.
    """
    return {"brands": kb.search_kb_brands(q)}


@router.get("/kb/fractions")
async def get_kb_fractions():
    """
    Returns 63 exact fraction lookup standards.
    """
    return {"fractions": kb.get_all_fractions()}


@router.get("/kb/thesaurus")
async def get_kb_thesaurus():
    """
    Returns trade jargon thesaurus terms.
    """
    return {"terms": kb.get_all_thesaurus()}


@router.get("/catalog")
async def get_catalog_items(page: int = 1, page_size: int = 50, search: str = ""):
    """
    Returns paginated items from the enriched 1000-item catalog.
    """
    csv_path = Path(__file__).resolve().parent.parent.parent.parent / "OmniSpec_Enriched_1000_Items_Delivery_252.csv"
    if not csv_path.exists():
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    items = []
    with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if search:
                s_lower = search.lower()
                if (s_lower in (row.get("Mfg_Part_Num", "")).lower() or 
                    s_lower in (row.get("BRAND_NAME", "")).lower() or 
                    s_lower in (row.get("Part_Desc", "")).lower()):
                    items.append(row)
            else:
                items.append(row)

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = items[start:end]

    return {
        "items": paginated,
        "total": total,
        "page": page,
        "page_size": page_size
    }


# ==========================================
# PHASE 7 ENDPOINTS (Provenance, DPI, Compatibility)
# ==========================================

@router.post("/provenance/dbom")
async def get_product_dbom(item: Dict[str, Any]):
    """
    Task 19: Generates complete Data Bill of Materials (DBOM) with cell-level provenance.
    """
    initial_state = ProductEnrichmentState(
        row_id=item.get("row_id", "row_dbom"),
        raw_mfg_part_num=item.get("Mfg_Part_Num", item.get("mfg_part_num", "")),
        raw_part_desc=item.get("Part_Desc", item.get("part_desc", "")),
        raw_e1_brand=item.get("E1_Brand", item.get("e1_brand", "")),
        raw_unilog_brand=item.get("Unilog_Brand", item.get("unilog_brand", "")),
        raw_dib_brand=item.get("DIB_Brand", item.get("dib_brand", "")),
        raw_part_manuf=item.get("Part_Manuf", item.get("part_manuf", "")),
        raw_sku=item.get("SKU", item.get("sku", "")),
        enable_llm=item.get("enable_llm", False)
    )

    final_state_dict = pipeline_graph.invoke(initial_state)
    state = ProductEnrichmentState(**final_state_dict)

    # Evaluate DPI risk score
    risk_result = DefectRiskScorer.evaluate_risk(state)
    
    # Generate DBOM
    dbom = DBOMService.generate_dbom(
        state=state,
        dpi_score=risk_result.dpi_score,
        risk_tier=risk_result.risk_tier
    )

    return {
        "success": True,
        "dbom": dbom.dict(),
        "risk_evaluation": risk_result.dict()
    }


@router.post("/audit/dpi")
async def evaluate_defect_probability(item: Dict[str, Any]):
    """
    Task 20: Evaluates Defect Probability Index (DPI) & Risk Queue factors for a SKU.
    """
    initial_state = ProductEnrichmentState(
        row_id=item.get("row_id", "row_dpi"),
        raw_mfg_part_num=item.get("Mfg_Part_Num", item.get("mfg_part_num", "")),
        raw_part_desc=item.get("Part_Desc", item.get("part_desc", "")),
        raw_e1_brand=item.get("E1_Brand", item.get("e1_brand", "")),
        raw_unilog_brand=item.get("Unilog_Brand", item.get("unilog_brand", "")),
        raw_dib_brand=item.get("DIB_Brand", item.get("dib_brand", "")),
        raw_part_manuf=item.get("Part_Manuf", item.get("part_manuf", "")),
        raw_sku=item.get("SKU", item.get("sku", ""))
    )

    final_state_dict = pipeline_graph.invoke(initial_state)
    state = ProductEnrichmentState(**final_state_dict)
    risk_result = DefectRiskScorer.evaluate_risk(state)

    return {
        "success": True,
        "mpn": state.mfr_part_number or state.clean_mfg_part_num,
        "brand_name": state.brand_name,
        "dpi": risk_result.dict()
    }


@router.post("/compatibility/evaluate")
async def evaluate_product_compatibility(payload: Dict[str, Any]):
    """
    Task 21: Evaluates mechanical, electrical, and dimensional compatibility between Product A and Product B.
    """
    product_a = payload.get("product_a", {})
    product_b = payload.get("product_b", {})
    
    result = CompatibilityEngine.evaluate_compatibility(product_a, product_b)
    return {
        "success": True,
        "result": result.dict()
    }


@router.get("/compatibility/substitutes")
async def get_product_substitutes(mpn: str = "", brand: str = "", desc: str = ""):
    """
    Task 21: Discovers direct OEM cross-brand substitutes and functional equivalents.
    """
    substitutes_resp = CompatibilityEngine.find_cross_brand_substitutes(mpn=mpn, brand=brand, desc=desc)
    return {
        "success": True,
        "data": substitutes_resp.dict()
    }


# ==========================================
# PHASE 8 ENDPOINTS (Parametric Search & Trade-Off Explainer)
# ==========================================

@router.post("/search/parametric")
async def search_catalog_parametric(payload: Dict[str, Any]):
    """
    Tasks 22 & 23: Compiles Natural Language into Parametric AST, queries catalog items,
    and returns Qualified matches alongside Disqualified trade-off explanations.
    """
    query = payload.get("query", "")
    enable_llm = payload.get("enable_llm", False)

    # Load master catalog items
    csv_path = Path(__file__).resolve().parent.parent.parent.parent / "OmniSpec_Enriched_1000_Items_Delivery_252.csv"
    items = []
    if csv_path.exists():
        with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            items = list(reader)

    # If no CSV on disk, use fallback seed items
    if not items:
        items = [
            {
                "Mfg_Part_Num": "PDSH4816AF",
                "BRAND_NAME": "FRIGIDAIRE®",
                "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
                "SHORT_DESC": "FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel 47 dBA 120V 15A",
                "Part_Desc": "PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA"
            },
            {
                "Mfg_Part_Num": "WDTS7024RZ",
                "BRAND_NAME": "Whirlpool®",
                "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
                "SHORT_DESC": "Whirlpool® Eco Series WDTS7024RZ Dishwasher, Built-in Mounting, Stainless Steel 41 dBA 120V 10A",
                "Part_Desc": "WDTS7024RZ Dishwasher SS - Display Only 120V 10A 41DBA"
            },
            {
                "Mfg_Part_Num": "SHX78B75UC",
                "BRAND_NAME": "Bosch®",
                "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
                "SHORT_DESC": "Bosch® 800 Series 24 in Built-In Dishwasher Stainless Steel 42 dBA 120V 12A",
                "Part_Desc": "Bosch 800 Series Dishwasher 42 dBA Stainless Steel 120V"
            },
            {
                "Mfg_Part_Num": "49-94-0101",
                "BRAND_NAME": "Milwaukee®",
                "Classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels",
                "SHORT_DESC": "Milwaukee® 4-1/2 in x .045 in x 7/8 in Metal Cut-Off Disc 13300 RPM",
                "Part_Desc": "4-1/2 in x .045 in x 7/8 in Cut Off Disc 13300 RPM"
            },
            {
                "Mfg_Part_Num": "DCS361B",
                "BRAND_NAME": "DEWALT®",
                "Classpath": "Tools & Instruments>Power Tools>Saws & Blades>Circular & Miter Saws",
                "SHORT_DESC": "DEWALT® 20V MAX* 7-1/4 IN Cordless Sliding Miter Saw Brushless 31.6 lbs",
                "Part_Desc": "DEWALT 20V MAX 7-1/4 IN Cordless Sliding Miter Saw Brushless 31.6 lbs"
            },
            {
                "Mfg_Part_Num": "558213",
                "BRAND_NAME": "Philips®",
                "Classpath": "Lighting & Electrical>Light Bulbs & Lamps>LED Light Bulbs",
                "SHORT_DESC": "Philips® 558213 LED Light Bulb, A19 Shape, 2700 K, Medium E26 Base 9.5W",
                "Part_Desc": "9.5W A19 LED 2700K Medium Base 60W Equivalent E26"
            },
            {
                "Mfg_Part_Num": "CPLG-38-BRS",
                "BRAND_NAME": "Mueller Industries®",
                "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings",
                "SHORT_DESC": "Mueller® 3/8 in Brass Pipe Coupling 150# NPT Threaded",
                "Part_Desc": "3/8 CPLG BRS 150# Female NPT Coupler"
            }
        ]

    response = ParametricSearchEngine.execute_search(
        query=query,
        catalog_items=items,
        enable_llm=enable_llm
    )

    return {
        "success": True,
        "data": response.dict()
    }


# ==========================================
# PHASE 9 ENDPOINTS (Product Families & Assortment Gap Detector)
# ==========================================

@router.get("/families")
async def get_all_product_families():
    """
    Tasks 25 & 26: Discovers canonical Parent Product Families, decomposes MPN series,
    and flags missing contractor assortment sequence gaps.
    """
    csv_path = Path(__file__).resolve().parent.parent.parent.parent / "OmniSpec_Enriched_1000_Items_Delivery_252.csv"
    items = []
    if csv_path.exists():
        with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            items = list(reader)

    # If no CSV, use rich multi-family demonstration items
    if not items or len(items) < 5:
        items = [
            {"Mfg_Part_Num": "DCG413B", "BRAND_NAME": "DEWALT®", "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders", "SHORT_DESC": "DEWALT® 20V MAX* XR 4-1/2 in Brushless Angle Grinder (Tool Only)"},
            {"Mfg_Part_Num": "DCG413P2", "BRAND_NAME": "DEWALT®", "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders", "SHORT_DESC": "DEWALT® 20V MAX* XR 4-1/2 in Brushless Angle Grinder Kit (2x 5.0Ah Batteries)"},
            {"Mfg_Part_Num": "DCG413R2", "BRAND_NAME": "DEWALT®", "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders", "SHORT_DESC": "DEWALT® 20V/60V MAX* FlexVolt 4-1/2 in Grinder Kit (2x 6.0Ah Batteries)"},
            {"Mfg_Part_Num": "SHX78B75UC", "BRAND_NAME": "Bosch®", "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "SHORT_DESC": "Bosch® 800 Series 24 in Built-In Dishwasher Stainless Steel 42 dBA"},
            {"Mfg_Part_Num": "SHX78B76UC", "BRAND_NAME": "Bosch®", "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "SHORT_DESC": "Bosch® 800 Series 24 in Built-In Dishwasher Black Stainless Steel 42 dBA"},
            {"Mfg_Part_Num": "CPLG-14-BRS", "BRAND_NAME": "Mueller Industries®", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings", "SHORT_DESC": "Mueller® 1/4 in Brass Pipe Coupling 150# NPT Threaded"},
            {"Mfg_Part_Num": "CPLG-38-BRS", "BRAND_NAME": "Mueller Industries®", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings", "SHORT_DESC": "Mueller® 3/8 in Brass Pipe Coupling 150# NPT Threaded"},
            {"Mfg_Part_Num": "CPLG-34-BRS", "BRAND_NAME": "Mueller Industries®", "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings", "SHORT_DESC": "Mueller® 3/4 in Brass Pipe Coupling 150# NPT Threaded"}
        ]

    resp = FamilyClusteringEngine.discover_product_families(items)
    return {
        "success": True,
        "data": resp.dict()
    }



