import asyncio
import io
import json
import os
import sys
from pathlib import Path
import pandas as pd
from fastapi import UploadFile

# Ensure repository root is on sys.path regardless of execution directory
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == "test_and_result" else CURRENT_DIR
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.db.duckdb_client import kb
from backend.app.api.routes import enrich_batch_csv_json


async def run_pipeline():
    print("===========================================================================")
    print("[OmniSpec AI] Running Complete 10-Agent Swarm for test.csv")
    print("===========================================================================")

    # 1. Locate test.csv in test_and_result/ or repository root
    test_csv_path = CURRENT_DIR / "test.csv"
    if not test_csv_path.exists():
        test_csv_path = REPO_ROOT / "test.csv"
    if not test_csv_path.exists():
        test_csv_path = Path("test.csv")

    if not test_csv_path.exists():
        raise FileNotFoundError(f"Could not locate test.csv in {CURRENT_DIR} or {REPO_ROOT}")

    print(f"[OmniSpec] Ingesting test dataset from: {test_csv_path}")

    # 2. Read test.csv into UploadFile format
    with open(test_csv_path, "rb") as f:
        file_bytes = f.read()

    upload_file = UploadFile(
        filename=test_csv_path.name,
        file=io.BytesIO(file_bytes)
    )

    # 3. Execute 10-Agent Swarm
    res = await enrich_batch_csv_json(upload_file)
    processed_records = res.get("records", [])
    print(f"\n[OmniSpec] Enriched {len(processed_records)} items through 10-Agent Swarm.")

    # 4. Clean delivery records for exact 252-column export (exclude internal _* metadata fields)
    clean_delivery_records = []
    for rec in processed_records:
        clean_rec = {k: v for k, v in rec.items() if not k.startswith("_")}
        clean_delivery_records.append(clean_rec)

    df_out = pd.DataFrame(clean_delivery_records)
    print(f"[OmniSpec] Exact Delivery Column Count: {len(df_out.columns)} Columns (Standard 252)")
    
    # Save CSV, XLSX, and JSON directly in CURRENT_DIR (test_and_result/)
    out_csv = CURRENT_DIR / "output.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"[OmniSpec] Saved 252-Column CSV Delivery Format to: {out_csv.resolve()}")

    out_xlsx = CURRENT_DIR / "output.xlsx"
    df_out.to_excel(out_xlsx, index=False)
    print(f"[OmniSpec] Saved 252-Column Excel Delivery Format to: {out_xlsx.resolve()}")

    out_json = CURRENT_DIR / "output.json"
    with open(out_json, "w", encoding="utf-8") as jf:
        json.dump(res, jf, indent=2)
    print(f"[OmniSpec] Saved Complete Output JSON to: {out_json.resolve()}")

    # 5. Print summary audit
    print("\n===========================================================================")
    print("ENRICHMENT SUMMARY & ATTRIBUTE AUDIT")
    print("===========================================================================")
    for idx, rec in enumerate(processed_records, 1):
        mpn = rec.get("Mfg_Part_Num", "Unknown")
        brand = rec.get("BRAND_NAME", "Unknown")
        pname = rec.get("PRODUCT_NAME", rec.get("Fine", "Product"))
        mfr_url = rec.get("MFR_URL", "N/A")
        
        attr_count = sum(1 for i in range(1, 51) if str(rec.get(f"ATTRIBUTE_VALUE {i}", "")).strip())
        print(f"\n[{idx}] MPN: {mpn} | Brand: {brand} | Product: {pname}")
        print(f"    MFR URL: {mfr_url}")
        print(f"    Populated Attributes: {attr_count}/50")
        
        print("    Sample Attributes:")
        for slot in range(1, min(15, attr_count + 1)):
            lbl = rec.get(f"ATTRIBUTE_LABEL {slot}", "")
            val = rec.get(f"ATTRIBUTE_VALUE {slot}", "")
            uom = rec.get(f"ATTRIBUTE_UOM {slot}", "")
            uom_str = f" [{uom}]" if uom else " [No UOM]"
            print(f"      * Slot {slot:02d}: {lbl} = {val}{uom_str}")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
