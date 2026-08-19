import csv
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..schemas.state_schema import ProductEnrichmentState
from ..agents.graph import create_omnispec_graph
from ..schemas.delivery_schema import DeliveryProductRecord
from ..db.duckdb_client import kb
from ..services.excel_exporter import ExcelDeliveryExporter
from ..services.vision_spec_rag import VisionSpecSheetRAG

router = APIRouter()
pipeline_graph = create_omnispec_graph()


class ReviewerOverridePayload(BaseModel):
    mpn: str
    brand_name: str
    manufacturer_name: str
    trade_name: Optional[str] = ""
    override_data: Optional[Dict[str, Any]] = None
    reviewer_notes: Optional[str] = "Human reviewer manual validation"


@router.post("/enrich/single", response_model=Dict[str, Any])
async def enrich_single_item(item: Dict[str, Any]):
    """
    Enriches a single raw catalog row through the 9-Agent LangGraph Swarm.
    """
    initial_state = ProductEnrichmentState(
        row_id=item.get("row_id", "row_1"),
        raw_mfg_part_num=item.get("Mfg_Part_Num", item.get("mfg_part_num", "")),
        raw_part_desc=item.get("Part_Desc", item.get("part_desc", "")),
        raw_e1_brand=item.get("E1_Brand", item.get("e1_brand", "")),
        raw_unilog_brand=item.get("Unilog_Brand", item.get("unilog_brand", "")),
        raw_dib_brand=item.get("DIB_Brand", item.get("dib_brand", "")),
        raw_part_manuf=item.get("Part_Manuf", item.get("part_manuf", "")),
        raw_sku=item.get("SKU", item.get("sku", "")),
        enable_llm=item.get("enable_llm", False)
    )

    final_state = pipeline_graph.invoke(initial_state)
    delivery_dict = final_state["delivery_record"].to_delivery_dict() if final_state.get("delivery_record") else {}

    return {
        "success": True,
        "overall_confidence": final_state.get("overall_confidence", 1.0),
        "needs_hitl_review": final_state.get("needs_hitl_review", False),
        "violations": final_state.get("integrity_violations", []),
        "traces": [t.dict() for t in final_state.get("traces", [])],
        "delivery_record": delivery_dict
    }


@router.post("/enrich/batch")
async def enrich_batch_csv(file: UploadFile = File(...)):
    """
    Upload a raw CSV feed (e.g. 1000 items) and receive full 252-column enriched CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8", errors="ignore")))

    enriched_records = []
    for idx, row in enumerate(reader):
        initial_state = ProductEnrichmentState(
            row_id=f"row_{idx+1}",
            raw_mfg_part_num=row.get("Mfg_Part_Num", ""),
            raw_part_desc=row.get("Part_Desc", ""),
            raw_e1_brand=row.get("E1_Brand", ""),
            raw_unilog_brand=row.get("Unilog_Brand", ""),
            raw_dib_brand=row.get("DIB_Brand", ""),
            raw_part_manuf=row.get("Part_Manuf", "")
        )
        final_state = pipeline_graph.invoke(initial_state)
        if final_state.get("delivery_record"):
            enriched_records.append(final_state["delivery_record"].to_delivery_dict())

    if not enriched_records:
        raise HTTPException(status_code=400, detail="No valid records found in uploaded file.")

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
    Upload a CSV file and receive an array of enriched 252-column JSON records.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8", errors="ignore")))

    enriched_records = []
    for idx, row in enumerate(reader):
        initial_state = ProductEnrichmentState(
            row_id=f"row_{idx+1}",
            raw_mfg_part_num=row.get("Mfg_Part_Num", row.get("mfg_part_num", "")),
            raw_part_desc=row.get("Part_Desc", row.get("part_desc", "")),
            raw_e1_brand=row.get("E1_Brand", row.get("e1_brand", "")),
            raw_unilog_brand=row.get("Unilog_Brand", row.get("unilog_brand", "")),
            raw_dib_brand=row.get("DIB_Brand", row.get("dib_brand", "")),
            raw_part_manuf=row.get("Part_Manuf", row.get("part_manuf", ""))
        )
        final_state = pipeline_graph.invoke(initial_state)
        if final_state.get("delivery_record"):
            rec_dict = final_state["delivery_record"].to_delivery_dict()
            rec_dict["_confidence"] = final_state.get("overall_confidence", 1.0)
            rec_dict["_needs_hitl"] = final_state.get("needs_hitl_review", False)
            enriched_records.append(rec_dict)

    return {
        "success": True,
        "count": len(enriched_records),
        "records": enriched_records
    }


@router.post("/enrich/export-excel")
async def export_excel_workbook():
    """
    Exports the enriched 1000-item catalog as a multi-sheet, styled .xlsx workbook.
    """
    csv_path = Path(__file__).resolve().parent.parent.parent.parent / "OmniSpec_Enriched_1000_Items_Delivery_252.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Enriched catalog not found. Run enrichment batch first.")

    records = []
    with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    excel_bytes = ExcelDeliveryExporter.export_delivery_workbook(records)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=OmniSpec_Enriched_1000_Catalog_Master_252.xlsx"}
    )


@router.post("/hitl/override")
async def save_reviewer_override(payload: ReviewerOverridePayload):
    """
    Active Learning Feedback Loop: Saves manual human corrections into DuckDB
    so subsequent swarm executions automatically adopt the approved master entities.
    """
    override_dict = payload.override_data or {}
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
