import time
from typing import Dict, Any
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..schemas.delivery_schema import DeliveryProductRecord
from ..services.audit_engine import QualityAuditEngine
from ..orchestrator.attribute_finalizer_orchestrator import AttributeFinalizerOrchestrator
from ..db.duckdb_client import kb
from ..core.logging import logger


class QualityAuditAgent:
    """
    Agent 9: Quality Audit, Lineage Tracer & HITL Orchestrator Agent
    Constructs the final 252-column delivery record, executes 12 automated integrity rules,
    computes weighted confidence scores (0 - 100%), and routes low-confidence SKUs to HITL.
    """

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        # Build complete 252-Column Delivery Record
        rec = DeliveryProductRecord(
            mfr_url=state.mfr_url,
            ref_url_1=state.ref_urls[0] if len(state.ref_urls) > 0 else "",
            ref_url_2=state.ref_urls[1] if len(state.ref_urls) > 1 else "",
            ref_url_3=state.ref_urls[2] if len(state.ref_urls) > 2 else "",
            ref_url_4=state.ref_urls[3] if len(state.ref_urls) > 3 else "",
            ref_url_5=state.ref_urls[4] if len(state.ref_urls) > 4 else "",
            part_number=state.raw_sku or state.clean_mfg_part_num or "10001",
            dept=state.dept,
            class_name=state.class_name,
            fine=state.fine,
            sku=state.raw_sku,
            mfg_part_num=state.clean_mfg_part_num or state.raw_mfg_part_num,
            part_desc=state.raw_part_desc,
            e1_brand=state.raw_e1_brand,
            unilog_brand=state.raw_unilog_brand,
            dib_brand=state.raw_dib_brand,
            part_manuf=state.raw_part_manuf,
            manufacturer_name=state.manufacturer_name,
            brand_name=state.brand_name,
            trade_name=state.trade_name,
            manufacturer_part_number=state.mfr_part_number or state.clean_mfg_part_num,
            alternate_part_number=state.alt_part_number,
            classpath=state.classpath,
            mobile_desc=state.mobile_desc,
            invoice_desc=state.invoice_desc,
            short_desc=state.short_desc,
            long_desc1=state.long_desc1,
            retail_desc=state.retail_desc,
            marketing_description=state.marketing_desc,
            with_features=state.with_features,
            standard_approvals=state.standard_approvals,
            includes=state.includes,
            application=state.application,
            prop_65=state.prop_65 or "No",
            product_name=state.product_name,
            attributes=state.attributes,
            unspsc=state.unspsc,
            warranty=state.warranty or "1 Year Manufacturer, 1 Year Labor and Parts",
            length=state.dimensions.get("LENGTH", ""),
            length_uom=state.dimensions.get("LENGTH_UOM", "in" if state.dimensions.get("LENGTH") else ""),
            width=state.dimensions.get("WIDTH", ""),
            width_uom=state.dimensions.get("WIDTH_UOM", "in" if state.dimensions.get("WIDTH") else ""),
            height=state.dimensions.get("HEIGHT", ""),
            height_uom=state.dimensions.get("HEIGHT_UOM", "in" if state.dimensions.get("HEIGHT") else ""),
            weight=state.dimensions.get("WEIGHT", ""),
            weight_uom=state.dimensions.get("WEIGHT_UOM", "lb" if state.dimensions.get("WEIGHT") else ""),
            volume=state.dimensions.get("VOLUME", ""),
            volume_uom=state.dimensions.get("VOLUME_UOM", ""),
            selling_qty=state.packaging_specs.get("Selling Qty", "1"),
            selling_uom=state.packaging_specs.get("Selling UOM", "Each"),
            standard_packaging_info=state.packaging_specs.get("Standard Packaging Information", "1 Each"),
            product_image=state.digital_assets.get("Product Image", ""),
            alternate_image_1=state.digital_assets.get("Alternate Image 1", ""),
            alternate_image_2=state.digital_assets.get("Alternate Image 2", ""),
            alternate_image_3=state.digital_assets.get("Alternate Image 3", ""),
            alternate_image_4=state.digital_assets.get("Alternate Image 4", ""),
            specification_sheet=state.digital_assets.get("Specification Sheet", ""),
            instruction_manual=state.digital_assets.get("Instruction/Installation Manual", ""),
            owners_manual=state.digital_assets.get("Owners/User Manual", ""),
            sds=state.digital_assets.get("SDS", ""),
            warranty_info=state.digital_assets.get("Warranty Information", state.warranty or "1 Year Manufacturer, 1 Year Labor and Parts"),
            rohs=state.digital_assets.get("RoHS", "RoHS Compliant"),
            country_of_origin=state.digital_assets.get("Country Of Origin", "United States"),
            discontinued=state.digital_assets.get("Discontinued", "No"),
            actual_image=state.digital_assets.get("Actual Image (Yes/No)", "Yes")
        )

        # Finalize all 252 catalog delivery headers via AttributeFinalizerOrchestrator
        rec = AttributeFinalizerOrchestrator.finalize_record(state, rec)

        # Allocate bullet items 1 to 20
        for idx, feat in enumerate(state.item_features[:20], 1):
            setattr(rec, f"item_features_{idx}", feat)

        # Run Evidence-Aware confidence audit
        mpn_key = state.clean_mfg_part_num or state.raw_mfg_part_num
        is_cached = getattr(state, "is_cached", False) or bool(kb.get_override(mpn_key))
        conf, violations, hitl_reasons, evidence_breakdown = QualityAuditEngine.audit_record(rec, is_cached=is_cached)
        
        # If cached: zero HITL needed (100% confidence); if uncached: requires human review & approval
        if is_cached:
            needs_hitl = False
        else:
            needs_hitl = True
            if not hitl_reasons:
                hitl_reasons.append("UNCACHED_RECORD: First-time ingestion pending human verification")

        trace = AgentTrace(
            agent_name="Agent 9: Quality Audit & HITL",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Evidence-Aware Confidence: {conf * 100:.1f}%" + (" (100% Verified Cache)" if is_cached else ""),
                f"Evidence Vector: Retrieval={evidence_breakdown['retrieval_quality']*100:.0f}%, Authority={evidence_breakdown['evidence_authority']*100:.0f}%, Consistency={evidence_breakdown['extraction_consistency']*100:.0f}%, Agreement={evidence_breakdown['cross_source_agreement']*100:.0f}%, DetVal={evidence_breakdown['deterministic_validation']*100:.0f}%, Penalties=-{evidence_breakdown['penalties_applied']*100:.0f}%",
                f"Routing to HITL: {needs_hitl}" + (f" (Reasons: {'; '.join(hitl_reasons[:2])})" if hitl_reasons else "")
            ],
            extracted_data={
                "confidence_score": conf,
                "evidence_breakdown": evidence_breakdown,
                "violations": violations,
                "hitl_reasons": hitl_reasons,
                "needs_hitl": needs_hitl
            }
        )

        return {
            "overall_confidence": conf,
            "integrity_violations": violations,
            "needs_hitl_review": needs_hitl,
            "delivery_record": rec,
            "traces": state.traces + [trace]
        }
