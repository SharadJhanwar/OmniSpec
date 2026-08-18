import time
from typing import Dict, Any
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..schemas.delivery_schema import DeliveryProductRecord
from ..services.audit_engine import QualityAuditEngine
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
            part_number=state.raw_sku or "10001",
            dept=state.dept,
            class_name=state.class_name,
            fine=state.fine,
            sku=state.raw_sku,
            mfg_part_num=state.clean_mfg_part_num,
            part_desc=state.raw_part_desc,
            e1_brand=state.raw_e1_brand,
            unilog_brand=state.raw_unilog_brand,
            dib_brand=state.raw_dib_brand,
            part_manuf=state.raw_part_manuf,
            manufacturer_name=state.manufacturer_name,
            brand_name=state.brand_name,
            trade_name=state.trade_name,
            manufacturer_part_number=state.mfr_part_number,
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
            prop_65=state.prop_65,
            product_name=state.product_name,
            attributes=state.attributes,
            warranty=state.warranty,
            length=state.dimensions.get("LENGTH", ""),
            length_uom=state.dimensions.get("LENGTH_UOM", ""),
            width=state.dimensions.get("WIDTH", ""),
            width_uom=state.dimensions.get("WIDTH_UOM", ""),
            height=state.dimensions.get("HEIGHT", ""),
            height_uom=state.dimensions.get("HEIGHT_UOM", ""),
            selling_qty=state.packaging_specs.get("Selling Qty", "1"),
            selling_uom=state.packaging_specs.get("Selling UOM", "Each"),
            product_image=state.digital_assets.get("Product Image", ""),
            alternate_image_1=state.digital_assets.get("Alternate Image 1", ""),
            alternate_image_2=state.digital_assets.get("Alternate Image 2", ""),
            alternate_image_3=state.digital_assets.get("Alternate Image 3", ""),
            alternate_image_4=state.digital_assets.get("Alternate Image 4", ""),
            specification_sheet=state.digital_assets.get("Specification Sheet", ""),
            instruction_manual=state.digital_assets.get("Instruction/Installation Manual", ""),
            owners_manual=state.digital_assets.get("Owners/User Manual", ""),
            sds=state.digital_assets.get("SDS", ""),
            country_of_origin=state.digital_assets.get("Country Of Origin", "United States"),
            discontinued=state.digital_assets.get("Discontinued", "No"),
            actual_image=state.digital_assets.get("Actual Image (Yes/No)", "Yes")
        )

        # Allocate bullet items 1 to 20
        for idx, feat in enumerate(state.item_features[:20], 1):
            setattr(rec, f"item_features_{idx}", feat)

        # Run 12-point integrity audit
        conf, violations = QualityAuditEngine.audit_record(rec)
        needs_hitl = conf < 0.85 or len(violations) > 0

        trace = AgentTrace(
            agent_name="Agent 9: Quality Audit & HITL",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Overall Record Confidence: {conf * 100}%",
                f"Violations: {len(violations)}",
                f"Routing to HITL: {needs_hitl}"
            ],
            extracted_data={
                "confidence_score": conf,
                "violations": violations,
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
