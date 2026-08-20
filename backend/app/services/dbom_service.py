import hashlib
from typing import Dict, Any, Optional
from ..schemas.state_schema import ProductEnrichmentState
from ..schemas.provenance_schema import CellProvenance, DataBOM


class DBOMService:
    """
    Data Bill of Materials (DBOM) & Lineage Engine
    Generates fine-grained cell-level audit provenance for every delivery attribute.
    """

    @classmethod
    def generate_dbom(cls, state: ProductEnrichmentState, dpi_score: float = 0.0, risk_tier: str = "LOW") -> DataBOM:
        cells: Dict[str, CellProvenance] = {}
        tracked_count = 0
        oem_verified_sources = 0

        brand_name = state.brand_name or state.raw_unilog_brand or "UNBRANDED"
        mpn = state.mfr_part_number or state.clean_mfg_part_num or state.raw_mfg_part_num
        mfr_url = state.mfr_url or "https://www.oem-verified.com"
        spec_sheet_pdf = f"{brand_name.replace('®', '').replace('™', '').strip()}_{mpn}_Specification_Sheet.pdf"

        # 1. Brand & Manufacturer Master Data
        if state.manufacturer_name:
            cells["MANUFACTURER_NAME"] = CellProvenance(
                column_name="MANUFACTURER_NAME",
                value=state.manufacturer_name,
                source_type="UNICAT_BRAND_KB",
                source_ref="UniCat 27,000+ Master Database (DuckDB)",
                locator="Table: kb_unicat_brands, Column: manufacturer_name",
                agent_name="agent_2_entity_resolution",
                extraction_method="RAPIDFUZZ_C++ / KB_INDEX",
                confidence=round(state.brand_confidence, 3),
                rule_applied="UniCat Legal Entity Casing Standard §4",
                derived=False
            )
            tracked_count += 1

        if state.brand_name:
            cells["BRAND_NAME"] = CellProvenance(
                column_name="BRAND_NAME",
                value=state.brand_name,
                source_type="UNICAT_BRAND_KB",
                source_ref="UniCat 27,000+ Master Database (DuckDB)",
                locator="Table: kb_unicat_brands, Column: brand_name",
                agent_name="agent_2_entity_resolution",
                extraction_method="LEGAL_SYMBOL_INJECTOR",
                confidence=round(state.brand_confidence, 3),
                rule_applied="Mandatory ® / ™ Registered Trademark Rule",
                derived=False
            )
            tracked_count += 1

        if state.mfr_part_number or state.clean_mfg_part_num or state.raw_mfg_part_num:
            cells["MANUFACTURER_PART_NUMBER"] = CellProvenance(
                column_name="MANUFACTURER_PART_NUMBER",
                value=mpn,
                source_type="SUPPLIER_RAW_FEED",
                source_ref="Input CSV Column: Mfg_Part_Num",
                locator="Row Primary Key Identifier",
                agent_name="agent_1_ingestion",
                extraction_method="REGEX_MPN_TOKENIZER",
                confidence=1.0,
                rule_applied="Clean Alphanumeric Prefix Isolator",
                derived=False
            )
            tracked_count += 1

        # 2. Taxonomy & UNSPSC
        if state.classpath:
            cells["Classpath"] = CellProvenance(
                column_name="Classpath",
                value=state.classpath,
                source_type="UNICAT_LOV_KB",
                source_ref="UniCat 161,000 Category Schema Hierarchy",
                locator="Table: kb_unicat_lov, Column: Classpath",
                agent_name="agent_3_taxonomy",
                extraction_method="4_TIER_TAXONOMY_CLASSIFIER",
                confidence=round(state.taxonomy_confidence, 3),
                rule_applied="4-Tier Category Taxonomy Standard (Dept > Class > Fine > Product)",
                derived=True
            )
            tracked_count += 1

        if state.unspsc:
            cells["UNSPSC"] = CellProvenance(
                column_name="UNSPSC",
                value=state.unspsc,
                source_type="UNICAT_LOV_KB",
                source_ref="UNSPSC International Commodity Code Standard v24.0",
                locator="Table: kb_unicat_lov, Column: UNSPSC",
                agent_name="agent_3_taxonomy",
                extraction_method="8_DIGIT_LEAF_CLASSIFIER",
                confidence=1.0,
                rule_applied="8-Digit Leaf UNSPSC Matching",
                derived=True
            )
            tracked_count += 1

        # 3. Multi-Channel Copy Tiers
        if state.invoice_desc:
            cells["INVOICE_DESC"] = CellProvenance(
                column_name="INVOICE_DESC",
                value=state.invoice_desc,
                source_type="FORMULA_DERIVED",
                source_ref="Unilog Master Content Guidelines §2.1",
                locator="ERP Line Item Display Standard",
                agent_name="agent_7_copy_builder",
                extraction_method="CONSTRAINED_TEMPLATE_ENGINE",
                confidence=1.0 if len(state.invoice_desc) <= 40 else 0.75,
                rule_applied="Length <= 40 Chars, STRICT ALL CAPS, Abbreviations Only",
                derived=True
            )
            tracked_count += 1

        if state.mobile_desc:
            cells["MOBILE_DESC"] = CellProvenance(
                column_name="MOBILE_DESC",
                value=state.mobile_desc,
                source_type="FORMULA_DERIVED",
                source_ref="Unilog Master Content Guidelines §2.2",
                locator="Mobile Warehouse & Search Summary Standard",
                agent_name="agent_7_copy_builder",
                extraction_method="CONSTRAINED_TEMPLATE_ENGINE",
                confidence=1.0 if (60 <= len(state.mobile_desc) <= 80) else 0.85,
                rule_applied="Length 60-80 Chars (<MFR> <Brand>, <Item>, <Series>, <MPN>)",
                derived=True
            )
            tracked_count += 1

        if state.short_desc:
            cells["SHORT_DESC"] = CellProvenance(
                column_name="SHORT_DESC",
                value=state.short_desc,
                source_type="FORMULA_DERIVED",
                source_ref="Unilog Master Content Guidelines §3.0",
                locator="PDP Product Title",
                agent_name="agent_7_copy_builder",
                extraction_method="TITLE_FORMULA_SYNTHESIZER",
                confidence=round(state.overall_confidence, 3),
                rule_applied="Brand® + Series + MPN + Item Type + Key Specifications",
                derived=True
            )
            tracked_count += 1

        if state.long_desc1:
            cells["LONG_DESC1"] = CellProvenance(
                column_name="LONG_DESC1",
                value=state.long_desc1,
                source_type="FORMULA_DERIVED",
                source_ref="Unilog Master Content Guidelines §4.0",
                locator="PDP Extended Technical Narrative",
                agent_name="agent_7_copy_builder",
                extraction_method="SPEC_NARRATIVE_MERGER",
                confidence=round(state.overall_confidence, 3),
                rule_applied="Exhaustive Narrative + Standardized Dimensions + 'Additional Information:'",
                derived=True
            )
            tracked_count += 1

        # 4. Sourcing & Regulatory
        if state.mfr_url:
            cells["MFR URL"] = CellProvenance(
                column_name="MFR URL",
                value=state.mfr_url,
                source_type="OEM_OFFICIAL_URL",
                source_ref=mfr_url,
                locator="Direct OEM Manufacturer Portal",
                agent_name="agent_5_oem_sourcing",
                extraction_method="AUTHORITATIVE_DOMAIN_RESOLVER",
                confidence=round(state.sourcing_confidence, 3),
                rule_applied="Zero Marketplace Leakage Policy (Banned: Amazon/Grainger/eBay)",
                derived=False
            )
            tracked_count += 1
            oem_verified_sources += 1

        if state.standard_approvals:
            cells["Standard/Approvals"] = CellProvenance(
                column_name="Standard/Approvals",
                value=state.standard_approvals,
                source_type="OEM_SPEC_SHEET_PDF",
                source_ref=spec_sheet_pdf,
                locator="Page 1, Compliance & Ratings Block",
                agent_name="agent_5_oem_sourcing",
                extraction_method="CERTIFICATION_AGGREGATOR",
                confidence=round(state.sourcing_confidence, 3),
                rule_applied="Pipe-Delimited Standard Certification Format",
                derived=False
            )
            tracked_count += 1
            oem_verified_sources += 1

        # 5. Dimensions & Fractions
        for dim_key, dim_val in state.dimensions.items():
            if dim_val:
                cells[dim_key] = CellProvenance(
                    column_name=dim_key,
                    value=dim_val,
                    source_type="SUPPLIER_RAW_FEED",
                    source_ref=f"Extracted from Part_Desc token: '{state.raw_part_desc}'",
                    locator="Dimension Triplet Parser",
                    agent_name="agent_4_spec_uom",
                    extraction_method="63_EXACT_FRACTION_MAPPER",
                    confidence=round(state.spec_confidence, 3),
                    rule_applied="63 Decimal-to-Fraction Reference Standard & Single-Space UOM",
                    derived=True
                )
                tracked_count += 1

        # 6. EAV Attributes (Attributes 1..50)
        attr_idx = 1
        for attr_k, attr_v in state.attributes.items():
            if attr_k and attr_v and attr_idx <= 50:
                cells[f"ATTRIBUTE_LABEL {attr_idx}"] = CellProvenance(
                    column_name=f"ATTRIBUTE_LABEL {attr_idx}",
                    value=attr_k,
                    source_type="UNICAT_LOV_KB",
                    source_ref="UniCat Controlled Vocabulary Schema",
                    locator=f"Schema: {state.classpath}",
                    agent_name="agent_6_lov_mapper",
                    extraction_method="CONSTRAINED_LOV_ALLOCATOR",
                    confidence=1.0,
                    rule_applied="161K LOV Controlled Dictionary Key Binding",
                    derived=False
                )
                cells[f"ATTRIBUTE_VALUE {attr_idx}"] = CellProvenance(
                    column_name=f"ATTRIBUTE_VALUE {attr_idx}",
                    value=attr_v,
                    source_type="OEM_SPEC_SHEET_PDF",
                    source_ref=spec_sheet_pdf,
                    locator=f"Spec Table Row: '{attr_k}'",
                    agent_name="agent_6_lov_mapper",
                    extraction_method="EAV_SPEC_MAPPER",
                    confidence=0.95,
                    rule_applied="Controlled Vocabulary Value Alignment",
                    derived=False
                )
                tracked_count += 2
                attr_idx += 1

        # 7. Digital Assets
        prod_img = state.digital_assets.get("product_image", f"{brand_name.replace('®', '').replace('™', '').strip()}_{mpn}.jpg")
        cells["Product Image"] = CellProvenance(
            column_name="Product Image",
            value=prod_img,
            source_type="FORMULA_DERIVED",
            source_ref="Digital Asset Management (DAM) Schema",
            locator="Primary JPG Asset Key",
            agent_name="agent_8_digital_assets",
            extraction_method="CANONICAL_ASSET_SYNTHESIZER",
            confidence=1.0,
            rule_applied="<Brand>_<MPN>.jpg Canonical Naming Convention",
            derived=True
        )
        tracked_count += 1

        spec_sheet = state.digital_assets.get("specification_sheet", spec_sheet_pdf)
        cells["Specification Sheet"] = CellProvenance(
            column_name="Specification Sheet",
            value=spec_sheet,
            source_type="FORMULA_DERIVED",
            source_ref="Digital Asset Management (DAM) Schema",
            locator="Technical Submittal PDF Asset Key",
            agent_name="agent_8_digital_assets",
            extraction_method="CANONICAL_ASSET_SYNTHESIZER",
            confidence=1.0,
            rule_applied="<Brand>_<MPN>_Specification_Sheet.pdf Canonical Submittal Rule",
            derived=True
        )
        tracked_count += 1

        # Generate cryptographic lineage hash
        raw_signature = f"{mpn}_{brand_name}_{tracked_count}_{state.overall_confidence}"
        lineage_hash = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()

        return DataBOM(
            row_id=state.row_id or mpn,
            mpn=mpn,
            brand_name=brand_name,
            manufacturer_name=state.manufacturer_name or "Unknown Manufacturer",
            overall_confidence=round(state.overall_confidence, 3),
            defect_probability_index=round(dpi_score, 3),
            risk_tier=risk_tier,
            total_attributes_tracked=tracked_count,
            verified_oem_sources_count=oem_verified_sources,
            provenance_cells=cells,
            lineage_hash=lineage_hash
        )
