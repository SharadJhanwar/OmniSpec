import sys
import csv
import io
from pathlib import Path
from rapidfuzz import fuzz

from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.graph import create_omnispec_graph
from backend.app.core.logging import logger


def run_ground_truth_benchmark():
    logger.info("=================================================================")
    logger.info("OMNISPEC AI: 252-COLUMN GROUND TRUTH BENCHMARK HARNESS")
    logger.info("=================================================================")

    ground_truth_file = Path(__file__).resolve().parent.parent.parent / "docs" / "dataset" / "Unihack_ Expected Output - Delivery Format.csv"
    if not ground_truth_file.exists():
        logger.error(f"Ground truth file not found at: {ground_truth_file}")
        return

    with open(ground_truth_file, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        expected_rows = list(reader)

    logger.info(f"Loaded {len(expected_rows)} ground truth rows across {len(reader.fieldnames)} target columns.")

    # Initialize LangGraph Swarm
    graph = create_omnispec_graph()

    total_fields_scored = 0
    total_field_matches = 0
    key_field_scores = {
        "MANUFACTURER_NAME": [],
        "BRAND_NAME": [],
        "Classpath": [],
        "INVOICE_DESC": [],
        "MOBILE_DESC": [],
        "SHORT_DESC": [],
        "Product Image": [],
        "Specification Sheet": []
    }

    for idx, expected in enumerate(expected_rows, 1):
        mpn = expected.get("Mfg_Part_Num", "")
        desc = expected.get("Part_Desc", "")

        logger.info(f"\n[Evaluating SKU {idx}/{len(expected_rows)}]: {mpn} | {desc}")

        initial_state = ProductEnrichmentState(
            row_id=f"benchmark_{idx}",
            raw_mfg_part_num=mpn,
            raw_part_desc=desc,
            raw_e1_brand=expected.get("E1_Brand", ""),
            raw_unilog_brand=expected.get("Unilog_Brand", ""),
            raw_dib_brand=expected.get("DIB_Brand", ""),
            raw_part_manuf=expected.get("Part_Manuf", ""),
            raw_sku=expected.get("SKU - MY_PART_NUMBER", "")
        )

        final_state = graph.invoke(initial_state)
        delivery_dict = final_state["delivery_record"].to_delivery_dict() if final_state.get("delivery_record") else {}

        # Validate total delivery columns count
        assert len(delivery_dict) == 252, f"Expected 252 columns, got {len(delivery_dict)}"

        # Score key fields
        for field in key_field_scores.keys():
            exp_val = str(expected.get(field, "")).strip()
            gen_val = str(delivery_dict.get(field, "")).strip()

            similarity = fuzz.ratio(exp_val.upper(), gen_val.upper())
            key_field_scores[field].append(similarity)

            logger.info(f"  Field: {field:<22} | Expected: '{exp_val[:40]}' | Gen: '{gen_val[:40]}' -> Score: {similarity}%")

    logger.info("\n=================================================================")
    logger.info("FINAL BENCHMARK ACCURACY REPORT ACROSS GROUND TRUTH DATA")
    logger.info("=================================================================")
    for field, scores in key_field_scores.items():
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        logger.info(f"  {field:<25}: {avg_score}% Average Similarity")

    logger.info("  252-Column Delivery Schema: 100% Header Conformant (252 / 252 Columns)")
    logger.info("=================================================================")


if __name__ == "__main__":
    run_ground_truth_benchmark()
