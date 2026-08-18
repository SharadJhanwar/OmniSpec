import csv
import io
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from ..schemas.state_schema import ProductEnrichmentState
from ..agents.graph import create_omnispec_graph
from ..schemas.delivery_schema import DeliveryProductRecord

router = APIRouter()
pipeline_graph = create_omnispec_graph()


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
        raw_sku=item.get("SKU", item.get("sku", ""))
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

    # Export to CSV stream
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
