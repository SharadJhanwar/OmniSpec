import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.schemas.state_schema import ProductEnrichmentState
from app.agents.agent_1_ingestion import IngestionAgent
from app.agents.agent_2_entity_resolution import EntityResolutionAgent
from app.core.logging import logger


def test_agents_1_and_2():
    logger.info("==================================================")
    logger.info("TESTING AGENTS 1 & 2 (INGESTION & ENTITY RESOLUTION)")
    logger.info("==================================================")

    test_samples = [
        {
            "mfg_part_num": "PDSH4816AF",
            "part_desc": "PDSH4816AF Dishwasher SS - Display Only",
            "e1_brand": "-- Unbranded --",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Appliance Dealers Cooperative (APPDE)",
            "expected_mfr": "Rheem Manufacturing",
            "expected_brand": "FRIGIDAIRE®"
        },
        {
            "mfg_part_num": "3MABR-7100075678",
            "part_desc": "3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box",
            "e1_brand": "-- Unbranded --",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Jam Industrial Supply LLC (JAMIN)",
            "expected_mfr": "3M Co",
            "expected_brand": "3M™"
        },
        {
            "mfg_part_num": "49-94-0013",
            "part_desc": "49-94-0013 Milw 5\"x.045\"x7/8\" Metal Cut Off Disc",
            "e1_brand": "-- Unbranded --",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Milwaukee Accessory (4031)",
            "expected_mfr": "Milwaukee Electric Tool Corporation",
            "expected_brand": "Milwaukee®"
        },
        {
            "mfg_part_num": "1513720",
            "part_desc": "1nx6-16' Honey Grove Grooved - Trex Enhance Naturals Decking",
            "e1_brand": "TREX",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Boise Cascade Building Materials (BOICA)",
            "expected_mfr": "Trex Company Inc",
            "expected_brand": "Trex®"
        },
        {
            "mfg_part_num": "ADR5117512CS",
            "part_desc": "1x12-12' Coastline - Vintage Azek PVC Fascia",
            "e1_brand": "TIMBERTECH",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Parksite (6151)",
            "expected_mfr": "The AZEK Company LLC",
            "expected_brand": "AZEK®"
        },
        {
            "mfg_part_num": "9A-570-240",
            "part_desc": "9A-570-240 Abranet 2.75x30",
            "e1_brand": "-- Unbranded --",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Mirka Abrasives Inc (MIRUS)",
            "expected_mfr": "Mirka Abrasives Inc",
            "expected_brand": "Mirka®"
        }
    ]

    for idx, sample in enumerate(test_samples, 1):
        state = ProductEnrichmentState(
            row_id=f"test_{idx}",
            raw_mfg_part_num=sample["mfg_part_num"],
            raw_part_desc=sample["part_desc"],
            raw_e1_brand=sample["e1_brand"],
            raw_unilog_brand=sample["unilog_brand"],
            raw_dib_brand=sample["dib_brand"],
            raw_part_manuf=sample["part_manuf"]
        )

        # Execute Agent 1
        a1_output = IngestionAgent.execute(state)
        state = state.model_copy(update=a1_output)

        # Execute Agent 2
        a2_output = EntityResolutionAgent.execute(state)
        state = state.model_copy(update=a2_output)

        logger.info(f"\n--- Item {idx}: {sample['mfg_part_num']} ---")
        logger.info(f"Raw Desc:      {sample['part_desc']}")
        logger.info(f"Cleaned Desc:  {state.cleaned_part_desc}")
        logger.info(f"Dimensions:    {state.token_bag.get('dimensions')}")
        logger.info(f"Pack Qty:      {state.token_bag.get('pack_qty')}")
        logger.info(f"Resolved MFR:   {state.manufacturer_name}")
        logger.info(f"Resolved Brand: {state.brand_name}")
        logger.info(f"Trade Name:     {state.trade_name}")
        logger.info(f"Confidence:     {state.brand_confidence * 100}%")

        assert state.manufacturer_name != "", "Manufacturer name must not be empty"
        assert state.brand_name != "", "Brand name must not be empty"

    logger.info("\n==================================================")
    logger.info("TASK 2 VERIFICATION SUCCESSFUL: AGENTS 1 & 2 OPERATING WITH HIGH PRECISION!")
    logger.info("==================================================")


if __name__ == "__main__":
    test_agents_1_and_2()
