import re
from typing import Dict, List, Tuple, Any
from ..schemas.delivery_schema import DeliveryProductRecord


class QualityAuditEngine:
    """
    Evidence-Aware Calibrated Confidence & Quality Governance Engine:

    confidence =
        retrieval_quality (20%)
      + evidence_authority (20%)
      + extraction_consistency (20%)
      + cross_source_agreement (20%)
      + deterministic_validation (20%)
      - contradictions_penalty
      - missing_required_fields_penalty
    """

    @classmethod
    def audit_record(cls, record: DeliveryProductRecord, is_cached: bool = False) -> Tuple[float, List[str], List[str], Dict[str, Any]]:
        """
        Audits a DeliveryProductRecord using the Evidence-Aware Confidence Formulation.
        - If is_cached=True: 100% confidence, zero violations, needs_hitl_review=False.
        - If is_cached=False: Evidence-aware calibrated score, needs_hitl_review=True for human verification.
        Returns:
            - overall_confidence: float (0.20 to 1.00)
            - integrity_violations: List[str]
            - hitl_reasons: List[str]
            - evidence_breakdown: Dict[str, Any]
        """
        if is_cached:
            return 1.00, [], [], {
                "retrieval_quality": 1.00,
                "evidence_authority": 1.00,
                "extraction_consistency": 1.00,
                "cross_source_agreement": 1.00,
                "deterministic_validation": 1.00,
                "penalties_applied": 0.00,
                "cache_hit": True
            }

        violations: List[str] = []
        hitl_reasons: List[str] = []

        brand_raw = (record.brand_name or "").strip()
        brand_clean = brand_raw.lower()
        mpn = (record.mfg_part_num or "").strip()
        desc = (record.part_desc or "").strip().lower()
        classpath = (record.classpath or "").strip()
        mfr_url = (record.mfr_url or "").strip().lower()

        # =========================================================
        # 1. Retrieval Quality (Weight: 20%)
        # =========================================================
        # Evaluates match quality between query, KB, and evidence
        if "®" in brand_raw or "™" in brand_raw or (len(brand_clean) > 2 and brand_clean in desc):
            retrieval_quality = 1.00
        elif len(brand_clean) >= 3 and brand_clean not in ["-- unbranded --", "unbranded", "unassigned", "none", ""]:
            retrieval_quality = 0.85
        elif brand_clean in ["-- unbranded --", "unbranded", "unassigned", "none", ""]:
            retrieval_quality = 0.40
        else:
            retrieval_quality = 0.50

        # =========================================================
        # 2. Evidence Authority (Weight: 20%)
        # =========================================================
        # Evaluates source trustworthiness (Tier 1: OEM PDF / Reg Brand, Tier 2: Web Domain, Tier 3: Unverified)
        if mfr_url.endswith(".pdf"):
            evidence_authority = 1.00
        elif ("®" in brand_raw or "™" in brand_raw) and (mfr_url.startswith("http://") or mfr_url.startswith("https://")):
            evidence_authority = 0.95
        elif mfr_url.startswith("http://") or mfr_url.startswith("https://"):
            evidence_authority = 0.80
        elif brand_clean and brand_clean not in ["-- unbranded --", "unbranded", "unassigned", ""]:
            evidence_authority = 0.60
        else:
            evidence_authority = 0.35

        # =========================================================
        # 3. Extraction Consistency (Weight: 20%)
        # =========================================================
        # Evaluates technical specification extraction & UOM validity
        attrs = record.attributes or {}
        populated_specs = 0
        for i in range(1, 51):
            lbl = attrs.get(f"ATTRIBUTE_LABEL {i}", "")
            val = attrs.get(f"ATTRIBUTE_VALUE {i}", "")
            if lbl and val and val != "":
                populated_specs += 1

        if populated_specs >= 4:
            extraction_consistency = 1.00
        elif populated_specs >= 2:
            extraction_consistency = 0.85
        elif populated_specs == 1:
            extraction_consistency = 0.70
        else:
            extraction_consistency = 0.45
            hitl_reasons.append("LOW_SPEC_DENSITY: Zero technical specifications were grounded from evidence")

        # =========================================================
        # 4. Cross-Source Agreement (Weight: 20%)
        # =========================================================
        # Evaluates consensus across input description, taxonomy, and brand
        prod_noun = (record.product_name or "").lower()
        parts = [p.strip().lower() for p in classpath.split(">")] if classpath else []

        agreement_score = 1.00
        if prod_noun and not any(prod_noun in p or p in prod_noun for p in parts + [desc]):
            agreement_score -= 0.30
            hitl_reasons.append(f"TAXONOMY_DISAGREEMENT: Product noun '{record.product_name}' not aligned with classpath")

        if brand_clean and brand_clean not in ["-- unbranded --", "unbranded"] and brand_clean not in desc:
            # External discovery consensus check
            agreement_score -= 0.10

        cross_source_agreement = max(0.40, agreement_score)

        # =========================================================
        # 5. Deterministic Validation (Weight: 20%)
        # =========================================================
        det_score = 1.00

        # INVOICE_DESC bounds: <= 40 chars, ALL CAPS
        if len(record.invoice_desc) > 40:
            violations.append(f"RULE_1_INVOICE_LENGTH: Invoice Desc has {len(record.invoice_desc)} chars (max 40 allowed)")
            hitl_reasons.append("INVOICE_DESC_OVERFLOW: Exceeds 40 character contract maximum")
            det_score -= 0.35

        if record.invoice_desc and not record.invoice_desc.isupper():
            violations.append("RULE_2_INVOICE_CASING: Invoice Desc must be strictly UPPERCASE")
            det_score -= 0.15

        # MOBILE_DESC bounds: 60 - 80 chars
        mob_len = len(record.mobile_desc)
        if mob_len > 0 and (mob_len < 60 or mob_len > 80):
            violations.append(f"RULE_3_MOBILE_LENGTH: Mobile Desc has {mob_len} chars (expected 60-80)")
            hitl_reasons.append(f"MOBILE_DESC_OUT_OF_BOUNDS: Length {mob_len} chars outside 60-80 window")
            det_score -= 0.25

        if record.product_image and not record.product_image.endswith(".jpg"):
            violations.append("RULE_7_IMAGE_EXTENSION: Product Image must end with .jpg")
            det_score -= 0.10

        if record.specification_sheet and not record.specification_sheet.endswith(".pdf"):
            violations.append("RULE_8_SPEC_PDF_EXTENSION: Specification Sheet must end with .pdf")
            det_score -= 0.10

        deterministic_validation = max(0.20, det_score)

        # =========================================================
        # PENALTIES: Contradictions & Missing Required Fields
        # =========================================================
        penalties = 0.0

        # 1. Contradictions: Check category mismatch (e.g. motor vs multimeter, valve vs fitting)
        if "motor" in desc and "multimeter" in prod_noun:
            penalties += 0.35
            violations.append("RULE_9_CATEGORY_CONTRADICTION: Motor classified as Multimeter")
            hitl_reasons.append("CRITICAL_CONTRADICTION: Electric Motor categorized under Testing Instruments")

        if "valve" in desc and "dishwasher" in prod_noun:
            penalties += 0.35
            violations.append("RULE_9_CATEGORY_CONTRADICTION: Valve classified as Dishwasher")
            hitl_reasons.append("CRITICAL_CONTRADICTION: Plumbing Valve categorized under Kitchen Appliances")

        # 2. Missing Required Fields
        if not mpn:
            penalties += 0.30
            violations.append("RULE_4_MISSING_MPN: Mfg_Part_Num is empty")
            hitl_reasons.append("MISSING_MPN: Mandatory part number is blank")

        if not classpath or len(parts) < 2:
            penalties += 0.25
            violations.append("RULE_5_MISSING_CLASSPATH: Classpath is missing or incomplete")
            hitl_reasons.append("MISSING_TAXONOMY: Classpath has fewer than 2 hierarchy levels")

        if not brand_clean or brand_clean in ["-- unbranded --", "unbranded", "unassigned", "none", ""]:
            penalties += 0.20
            violations.append("RULE_6_UNRESOLVED_BRAND: Product lacks verified OEM brand identity")
            hitl_reasons.append("UNRESOLVED_BRAND: Product lacks verified OEM brand identity")

        # =========================================================
        # Composite Evidence-Aware Confidence Calculation
        # =========================================================
        base_confidence = (
            0.20 * retrieval_quality +
            0.20 * evidence_authority +
            0.20 * extraction_consistency +
            0.20 * cross_source_agreement +
            0.20 * deterministic_validation
        )

        final_confidence = max(0.25, min(0.98, round(base_confidence - penalties, 2)))

        evidence_breakdown = {
            "retrieval_quality": round(retrieval_quality, 2),
            "evidence_authority": round(evidence_authority, 2),
            "extraction_consistency": round(extraction_consistency, 2),
            "cross_source_agreement": round(cross_source_agreement, 2),
            "deterministic_validation": round(deterministic_validation, 2),
            "penalties_applied": round(penalties, 2)
        }

        return final_confidence, violations, hitl_reasons, evidence_breakdown
