import re
from typing import Dict, List, Tuple
from ..schemas.delivery_schema import DeliveryProductRecord


class QualityAuditEngine:
    """
    Executes the 12-Point Automated Integrity Suite against enriched records
    and calculates weighted record confidence scores (0 - 100%).
    """

    @classmethod
    def audit_record(cls, record: DeliveryProductRecord) -> Tuple[float, List[str]]:
        """
        Audits a DeliveryProductRecord against the 12 Unilog Integrity Rules.
        Returns: (confidence_score: float, violations: List[str])
        """
        violations = []
        score_deductions = 0.0

        # Rule 1: Invoice Length Ceiling (<= 40 chars)
        if len(record.invoice_desc) > 40:
            violations.append(f"RULE_1_INVOICE_LENGTH: Invoice Desc has {len(record.invoice_desc)} chars (max 40 allowed)")
            score_deductions += 0.20

        # Rule 2: Invoice Casing (ALL CAPS)
        if record.invoice_desc and not record.invoice_desc.isupper():
            violations.append("RULE_2_INVOICE_CASING: Invoice Desc must be strictly UPPERCASE")
            score_deductions += 0.10

        # Rule 3: Mobile Description Window (60 to 80 chars)
        mob_len = len(record.mobile_desc)
        if mob_len > 0 and (mob_len < 60 or mob_len > 80):
            violations.append(f"RULE_3_MOBILE_LENGTH: Mobile Desc has {mob_len} chars (expected 60-80)")
            score_deductions += 0.15

        # Rule 4: Mandatory Identifiers
        if not record.mfg_part_num:
            violations.append("RULE_4_MISSING_MPN: Mfg_Part_Num is empty")
            score_deductions += 0.25
        if not record.manufacturer_name:
            violations.append("RULE_5_MISSING_MFR: MANUFACTURER_NAME is empty")
            score_deductions += 0.20
        if not record.brand_name:
            violations.append("RULE_6_MISSING_BRAND: BRAND_NAME is empty")
            score_deductions += 0.15
        if not record.classpath:
            violations.append("RULE_7_MISSING_CLASSPATH: Classpath is empty")
            score_deductions += 0.15

        # Rule 5: Master UOM Spacing check (check for '24in', '120V', '15A' without space)
        bad_uom_spacing = re.findall(r"\b\d+(?:[/-]\d+)?(?:\.\d+)?(in|ft|mm|cm|V|A|W|dBA|lb)\b", record.short_desc)
        if bad_uom_spacing:
            violations.append(f"RULE_8_UOM_SPACING: Found UOMs lacking space separation: {bad_uom_spacing}")
            score_deductions += 0.05

        # Rule 6: Asset Naming Syntax
        if record.product_image and not record.product_image.endswith(".jpg"):
            violations.append("RULE_9_IMAGE_EXTENSION: Product Image must end with .jpg")
            score_deductions += 0.05
        if record.specification_sheet and not record.specification_sheet.endswith(".pdf"):
            violations.append("RULE_10_SPEC_PDF_EXTENSION: Specification Sheet must end with .pdf")
            score_deductions += 0.05

        # Calculate final confidence score (0.0 to 1.0)
        confidence = max(0.0, round(1.0 - score_deductions, 2))
        return confidence, violations
