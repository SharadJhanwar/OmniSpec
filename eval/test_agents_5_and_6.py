import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.schemas.state_schema import ProductEnrichmentState
from app.agents.agent_1_ingestion import IngestionAgent
from app.agents.agent_2_entity_resolution import EntityResolutionAgent
from app.agents.agent_3_taxonomy import TaxonomyClassifierAgent
from app.agents.agent_4_spec_uom import SpecUOMExtractorAgent
from app.agents.agent_5_oem_sourcing import OEMSourcingRAGAgent
from app.agents.agent_6_lov_mapper import ConstrainedLOVMapperAgent
from app.core.logging import logger


def test_agents_5_and_6():
    logger.info("==================================================")
    logger.info("TESTING AGENTS 5 & 6 (OEM SOURCING & CONSTRAINED LOV MAPPER)")
    logger.info("==================================================")

    test_samples = [
        {
            "mfg_part_num": "PDSH4816AF",
            "part_desc": "PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA",
            "e1_brand": "-- Unbranded --",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Appliance Dealers Cooperative (APPDE)"
        },
        {
            "mfg_part_num": "WDTS7024RZ",
            "part_desc": "WDTS7024RZ Dishwasher SS - Display Only",
            "e1_brand": "-- Unbranded --",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Appliance Dealers Cooperative (APPDE)"
        },
        {
            "mfg_part_num": "49-94-0013",
            "part_desc": "49-94-0013 Milw 5\"x.045\"x7/8\" Metal Cut Off Disc",
            "e1_brand": "-- Unbranded --",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Milwaukee Accessory (4031)"
        },
        {
            "mfg_part_num": "1513720",
            "part_desc": "1nx6-16' Honey Grove Grooved - Trex Enhance Naturals Decking",
            "e1_brand": "TREX",
            "unilog_brand": "-- No Unilog Brand --",
            "dib_brand": "-- No DIB Brand --",
            "part_manuf": "Boise Cascade Building Materials (BOICA)"
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

        # Sequential execution
        state = state.model_copy(update=IngestionAgent.execute(state))
        state = state.model_copy(update=EntityResolutionAgent.execute(state))
        state = state.model_copy(update=TaxonomyClassifierAgent.execute(state))
        state = state.model_copy(update=SpecUOMExtractorAgent.execute(state))
        state = state.model_copy(update=OEMSourcingRAGAgent.execute(state))
        state = state.model_copy(update=ConstrainedLOVMapperAgent.execute(state))

        logger.info(f"\n--- Item {idx}: {sample['mfg_part_num']} ---")
        logger.info(f"MFR URL:          {state.mfr_url}")
        logger.info(f"Approvals:        {state.standard_approvals}")
        logger.info(f"With Features:    {state.with_features}")
        logger.info(f"Warranty:         {state.warranty}")

        # Display first 8 allocated attribute slots
        logger.info("Allocated Attributes (1..8):")
        for a_idx in range(1, 9):
            lbl = state.attributes.get(f"ATTRIBUTE_LABEL {a_idx}")
            val = state.attributes.get(f"ATTRIBUTE_VALUE {a_idx}")
            uom = state.attributes.get(f"ATTRIBUTE_UOM {a_idx}")
            if lbl:
                logger.info(f"  [{a_idx}] {lbl} = '{val}' (UOM: '{uom}')")

        assert state.mfr_url != "", "MFR URL must be populated"
        assert len(state.attributes) == 150, "Must contain exactly 150 attribute columns (50 triples)"

    logger.info("\n==================================================")
    logger.info("TASK 4 VERIFICATION SUCCESSFUL: AGENTS 5 & 6 OPERATING WITH FULL SCHEMA CONFORMANCE!")
    logger.info("==================================================")


if __name__ == "__main__":
    test_agents_5_and_6()
