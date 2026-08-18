import time
import re
from typing import Dict, Any
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..services.asset_synthesizer import DigitalAssetSynthesizer
from ..core.logging import logger


class DigitalAssetAgent:
    """
    Agent 8: Digital Asset Synthesizer & Document Classifier Agent
    Standardizes image filenames and technical documentation URLs
    according to canonical Unilog asset naming rules (<Brand>_<MPN>.<ext>).
    """

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        brand_name = state.brand_name or "UNBRANDED"
        mpn = state.clean_mfg_part_num or "ITEM"
        ref_urls = state.ref_urls or []

        # Synthesize standard image and PDF names
        media = DigitalAssetSynthesizer.synthesize_media_filenames(brand_name, mpn)

        # Classify and map technical document URLs
        instruction_manual = ""
        owners_manual = ""
        sds_url = ""

        for url in ref_urls:
            url_lower = url.lower()
            if "installation" in url_lower or "instruction" in url_lower:
                instruction_manual = url
            elif "owners-manual" in url_lower or "user-guide" in url_lower:
                owners_manual = url
            elif "sds" in url_lower or "safety-data" in url_lower:
                sds_url = url

        media["Instruction/Installation Manual"] = instruction_manual
        media["Owners/User Manual"] = owners_manual
        media["SDS"] = sds_url
        media["Country Of Origin"] = "United States"
        media["Discontinued"] = "No"

        trace = AgentTrace(
            agent_name="Agent 8: Digital Asset Synthesizer",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Primary Image: {media.get('Product Image')}",
                f"Spec Sheet: {media.get('Specification Sheet')}",
                f"Installation Manual: {'Attached' if instruction_manual else 'None'}"
            ],
            extracted_data=media
        )

        return {
            "digital_assets": media,
            "traces": state.traces + [trace]
        }
