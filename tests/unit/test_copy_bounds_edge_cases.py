import pytest
from backend.app.core.logging import logger
from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.agent_7_copy_builder import MultiChannelCopyAgent

def test_invoice_desc_strict_length_bound():
    """Verify that INVOICE_DESC is NEVER strictly greater than 40 characters and is ALWAYS ALL CAPS."""
    logger.info("Testing Agent 7 INVOICE_DESC <= 40 chars and ALL CAPS bounds...")
    
    test_states = [
        ProductEnrichmentState(
            brand_name="FRIGIDAIRE®",
            clean_mfg_part_num="PDSH4816AF",
            dimensions={"LENGTH": "24-1/4", "WIDTH": "24", "HEIGHT": "33-7/16"},
            extracted_specs={"VOLTS": "120", "AMPS": "15", "WASH_CYCLES": "5"},
            category_path="Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers"
        ),
        ProductEnrichmentState(
            brand_name="Milwaukee®",
            clean_mfg_part_num="49-94-0101",
            dimensions={"DIAMETER": "4-1/2", "THICKNESS": ".045", "ARBOR_SIZE": "7/8"},
            extracted_specs={"MATERIAL": "Metal", "ABRASIVE": "Aluminum Oxide"},
            category_path="Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels"
        ),
        ProductEnrichmentState(
            brand_name="Mueller Industries®",
            clean_mfg_part_num="CPLG-38-BRS",
            dimensions={"NOMINAL_SIZE": "3/8"},
            extracted_specs={"MATERIAL": "Brass", "PRESSURE_CLASS": "150#", "THREAD_TYPE": "FNPT"},
            category_path="Plumbing & Pumps>Pipe Fittings>Couplings"
        )
    ]
    
    for state in test_states:
        out = MultiChannelCopyAgent.execute(state)
        inv = out.get("invoice_desc", "")
        assert len(inv) <= 40, f"INVOICE_DESC exceeds 40 chars ({len(inv)}): '{inv}'"
        assert inv == inv.upper(), f"INVOICE_DESC is not ALL CAPS: '{inv}'"


def test_mobile_desc_strict_bracket_bounds():
    """Verify that MOBILE_DESC strictly lands in the 60 to 80 character target range."""
    logger.info("Testing Agent 7 MOBILE_DESC 60-80 character window bounds...")
    
    test_states = [
        ProductEnrichmentState(
            manufacturer_name="Rheem Manufacturing",
            brand_name="FRIGIDAIRE®",
            clean_mfg_part_num="PDSH4816AF",
            series="Professional Series",
            extracted_specs={"FINISH": "Stainless Steel"},
            category_path="Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers"
        ),
        ProductEnrichmentState(
            manufacturer_name="Milwaukee Tool",
            brand_name="Milwaukee®",
            clean_mfg_part_num="49-94-0101",
            series="Performance Plus",
            extracted_specs={"DIAMETER": "4-1/2 in", "ARBOR": "7/8 in"},
            category_path="Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels"
        ),
        ProductEnrichmentState(
            manufacturer_name="Philips Lighting",
            brand_name="Philips®",
            clean_mfg_part_num="558213",
            series="EcoVantage",
            extracted_specs={"WATTS": "9.5", "LUMENS": "800"},
            category_path="Lighting & Electrical>Light Bulbs & Lamps>LED Light Bulbs"
        )
    ]
    
    for state in test_states:
        out = MultiChannelCopyAgent.execute(state)
        mob = out.get("mobile_desc", "")
        assert 60 <= len(mob) <= 80, f"MOBILE_DESC outside 60-80 chars ({len(mob)}): '{mob}'"
