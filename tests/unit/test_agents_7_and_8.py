from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.agent_1_ingestion import IngestionAgent
from backend.app.agents.agent_2_entity_resolution import EntityResolutionAgent
from backend.app.agents.agent_3_taxonomy import TaxonomyClassifierAgent
from backend.app.agents.agent_4_spec_uom import SpecUOMExtractorAgent
from backend.app.agents.agent_5_oem_sourcing import OEMSourcingRAGAgent
from backend.app.agents.agent_6_lov_mapper import ConstrainedLOVMapperAgent
from backend.app.agents.agent_7_copy_builder import MultiChannelCopyAgent
from backend.app.agents.agent_8_digital_assets import DigitalAssetAgent
from backend.app.core.logging import logger


def test_agents_7_and_8():
    logger.info("==================================================")
    logger.info("TESTING AGENTS 7 & 8 (MULTI-CHANNEL COPY & DIGITAL ASSETS)")
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

        # Sequential execution 1 to 8
        state = state.model_copy(update=IngestionAgent.execute(state))
        state = state.model_copy(update=EntityResolutionAgent.execute(state))
        state = state.model_copy(update=TaxonomyClassifierAgent.execute(state))
        state = state.model_copy(update=SpecUOMExtractorAgent.execute(state))
        state = state.model_copy(update=OEMSourcingRAGAgent.execute(state))
        state = state.model_copy(update=ConstrainedLOVMapperAgent.execute(state))
        state = state.model_copy(update=MultiChannelCopyAgent.execute(state))
        state = state.model_copy(update=DigitalAssetAgent.execute(state))

        logger.info(f"\n--- Item {idx}: {sample['mfg_part_num']} ---")
        logger.info(f"INVOICE_DESC (<=40): {state.invoice_desc} ({len(state.invoice_desc)} chars)")
        logger.info(f"MOBILE_DESC (60-80): {state.mobile_desc} ({len(state.mobile_desc)} chars)")
        logger.info(f"SHORT_DESC (Title):  {state.short_desc}")
        logger.info(f"LONG_DESC1:          {state.long_desc1[:120]}...")
        logger.info(f"Product Image:       {state.digital_assets.get('Product Image')}")
        logger.info(f"Spec Sheet:          {state.digital_assets.get('Specification Sheet')}")
        logger.info(f"Features (1..{len(state.item_features)}): {state.item_features[:3]}")

        assert len(state.invoice_desc) <= 40, f"Invoice Desc exceeded 40 chars: '{state.invoice_desc}'"
        assert 60 <= len(state.mobile_desc) <= 80, f"Mobile Desc outside 60-80 chars: '{state.mobile_desc}' ({len(state.mobile_desc)} chars)"
        assert state.digital_assets.get("Product Image") != "", "Product image must be populated"

    logger.info("\n==================================================")
    logger.info("TASK 5 VERIFICATION SUCCESSFUL: AGENTS 7 & 8 PASSED ALL FORMULA & CHARACTER CONSTRAINTS!")
    logger.info("==================================================")


if __name__ == "__main__":
    test_agents_7_and_8()
