import time
import re
from typing import Dict, Any
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..services.asset_synthesizer import DigitalAssetSynthesizer
from ..services.evidence_discovery_service import EvidenceDiscoveryService
from ..core.logging import logger


class DigitalAssetAgent:
    """
    Agent 8: Digital Asset Synthesizer & Document Classifier Agent
    Discovers real product image URLs via DuckDuckGo Image Search.
    Falls back to canonical Unilog asset naming convention (<Brand>_<MPN>.ext)
    when live image search returns no results.
    """

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        brand_name = state.brand_name or "UNBRANDED"
        mpn = state.clean_mfg_part_num or state.raw_mfg_part_num or "ITEM"
        ref_urls = state.ref_urls or []

        # ------------------------------------------------------------------
        # 1. Attempt real image URL discovery via DuckDuckGo Image Search
        # ------------------------------------------------------------------
        real_images = []
        try:
            real_images = EvidenceDiscoveryService.discover_product_images(
                mpn=mpn,
                brand=brand_name,
                max_images=5
            )
            if real_images:
                logger.info(f"  [Agent 8] Image Discovery: {len(real_images)} real URLs found for {mpn}")
        except Exception as e:
            logger.debug(f"  [Agent 8] Image search error: {e}")

        # ------------------------------------------------------------------
        # 2. Build canonical filenames (used as fallback if no real images)
        # ------------------------------------------------------------------
        media = DigitalAssetSynthesizer.synthesize_media_filenames(brand_name, mpn)

        # ------------------------------------------------------------------
        # 3. Override with real image URLs if found
        # ------------------------------------------------------------------
        if real_images:
            media["Product Image"]    = real_images[0]
            media["Alternate Image 1"] = real_images[1] if len(real_images) > 1 else ""
            media["Alternate Image 2"] = real_images[2] if len(real_images) > 2 else ""
            media["Alternate Image 3"] = real_images[3] if len(real_images) > 3 else ""
            media["Alternate Image 4"] = real_images[4] if len(real_images) > 4 else ""
            media["Actual Image (Yes/No)"] = "Yes"
        else:
            # Canonical filenames already set by synthesize_media_filenames
            media["Actual Image (Yes/No)"] = "No"

        # ------------------------------------------------------------------
        # 4. Classify technical document URLs from ref_urls
        # ------------------------------------------------------------------
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
        media["Country Of Origin"] = state.country_of_origin or "United States"
        media["Discontinued"] = "No"

        # ------------------------------------------------------------------
        # 5. Trace
        # ------------------------------------------------------------------
        img_status = f"REAL URL: {media.get('Product Image')}" if real_images else f"CANONICAL: {media.get('Product Image')}"
        trace = AgentTrace(
            agent_name="Agent 8: Digital Asset Synthesizer",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Primary Image: {img_status}",
                f"Spec Sheet: {media.get('Specification Sheet')}",
                f"Installation Manual: {'Attached' if instruction_manual else 'None'}"
            ],
            extracted_data=media
        )

        return {
            "digital_assets": media,
            "traces": state.traces + [trace]
        }
