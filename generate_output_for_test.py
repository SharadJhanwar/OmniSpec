import asyncio
import io
import json
import os
import pandas as pd
from backend.app.db.duckdb_client import kb
from backend.app.api.routes import enrich_batch_csv_json
from fastapi import UploadFile

async def run_pipeline():
    print("===========================================================================")
    print("[OmniSpec AI] Running Complete 10-Agent Swarm for test.csv")
    print("===========================================================================")

    # 1. Ensure test.csv exists in root
    test_csv_path = "test.csv"
    if not os.path.exists(test_csv_path):
        if os.path.exists("test_and_result/test2.xlsx"):
            df_source = pd.read_excel("test_and_result/test2.xlsx")
            df_source.to_csv(test_csv_path, index=False)
            print(f"[OmniSpec] Converted test_and_result/test2.xlsx -> {test_csv_path}")
        elif os.path.exists("test_and_result/test2_enriched_252.csv"):
            df_source = pd.read_csv("test_and_result/test2_enriched_252.csv")
            df_source.to_csv(test_csv_path, index=False)
            print(f"[OmniSpec] Copied test2_enriched_252.csv -> {test_csv_path}")

    # 2. Read test.csv
    with open(test_csv_path, "rb") as f:
        file_bytes = f.read()

    upload_file = UploadFile(
        filename="test.csv",
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
    
    # Save CSV
    out_csv = "output.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"[OmniSpec] Saved 252-Column CSV Delivery Format to: {os.path.abspath(out_csv)}")

    # Save XLSX
    out_xlsx = "output.xlsx"
    df_out.to_excel(out_xlsx, index=False)
    print(f"[OmniSpec] Saved 252-Column Excel Delivery Format to: {os.path.abspath(out_xlsx)}")

    # Save JSON (preserves confidence, audit, and trace metadata)
    out_json = "output.json"
    with open(out_json, "w", encoding="utf-8") as jf:
        json.dump(res, jf, indent=2)
    print(f"[OmniSpec] Saved Complete Output JSON to: {os.path.abspath(out_json)}")

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
