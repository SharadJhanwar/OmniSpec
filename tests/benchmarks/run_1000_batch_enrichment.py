import sys
import csv
import time
from pathlib import Path

from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.graph import create_omnispec_graph
from backend.app.core.logging import logger


def run_batch_1000():
    logger.info("=================================================================")
    logger.info("OMNISPEC AI: PROCESSING 1,000 CATALOG ROWS AT SCALE")
    logger.info("=================================================================")

    input_file = Path(__file__).resolve().parent.parent.parent / "docs" / "dataset" / "Unihack_ Sample Dataset - Input.csv"
    output_file = Path(__file__).resolve().parent.parent.parent / "OmniSpec_Enriched_1000_Items_Delivery_252.csv"

    if not input_file.exists():
        logger.error(f"Input file not found at: {input_file}")
        return

    with open(input_file, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    logger.info(f"Loaded {len(raw_rows)} raw catalog rows to enrich.")

    graph = create_omnispec_graph()
    enriched_records = []
    t_start = time.perf_counter()

    for idx, row in enumerate(raw_rows, 1):
        initial_state = ProductEnrichmentState(
            row_id=f"row_{idx}",
            raw_mfg_part_num=row.get("Mfg_Part_Num", ""),
            raw_part_desc=row.get("Part_Desc", ""),
            raw_e1_brand=row.get("E1_Brand", ""),
            raw_unilog_brand=row.get("Unilog_Brand", ""),
            raw_dib_brand=row.get("DIB_Brand", ""),
            raw_part_manuf=row.get("Part_Manuf", "")
        )

        final_state = graph.invoke(initial_state)
        rec_dict = final_state["delivery_record"].to_delivery_dict() if final_state.get("delivery_record") else {}
        enriched_records.append(rec_dict)

        if idx % 200 == 0 or idx == len(raw_rows):
            elapsed = round(time.perf_counter() - t_start, 2)
            logger.info(f"Processed {idx}/{len(raw_rows)} rows ({round(idx/elapsed, 1)} rows/sec)...")

    # Write final 252-Column Delivery CSV
    if enriched_records:
        fieldnames = list(enriched_records[0].keys())
        with open(output_file, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_records)

        total_time = round(time.perf_counter() - t_start, 2)
        logger.info(f"\nSUCCESS: Exported {len(enriched_records)} fully enriched rows across {len(fieldnames)} columns.")
        logger.info(f"Saved delivery deliverable to: {output_file.name}")
        logger.info(f"Total Processing Time: {total_time}s ({round(len(enriched_records)/total_time, 1)} SKUs/second)")
        logger.info("=================================================================")


if __name__ == "__main__":
    run_batch_1000()
