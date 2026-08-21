from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class CellProvenance(BaseModel):
    """
    Fine-grained lineage metadata for an individual delivery cell
    """
    column_name: str
    value: str
    source_type: str = "FORMULA_DERIVED"  # OEM_SPEC_SHEET_PDF, OEM_OFFICIAL_URL, UNICAT_BRAND_KB, UNICAT_LOV_KB, SUPPLIER_RAW_FEED, ACTIVE_OVERRIDE, FORMULA_DERIVED
    source_ref: str = ""                   # e.g., "https://www.frigidaire.com/PDSH4816AF" or "UniCat 27K Master KB (Row 4201)"
    locator: str = ""                      # e.g., "Page 2, Table: Electrical Ratings, Row 3"
    agent_name: str = ""                   # e.g., "agent_2_entity_resolution"
    extraction_method: str = ""            # e.g., "RAPIDFUZZ_C++", "REGEX_TOKENIZER", "GPT4O_MINI_VISION", "TEMPLATE_ENGINE"
    confidence: float = 1.0                # 0.0 to 1.0
    rule_applied: str = ""                 # e.g., "Unilog Title Formula §3.1", "Master UOM Spacing Standard", "Exact Fraction Hash"
    derived: bool = False                  # True if calculated/inferred vs explicitly stated in input
    is_cached: bool = False                # True if retrieved from verified/approved cache (100% confidence)
    needs_hitl: bool = False               # True if variable is uncached / newly inferred
    hitl_reason: str = ""                  # Explanation if variable requires human review


class DataBOM(BaseModel):
    """
    Data Bill of Materials (DBOM) for a complete 252-column product record
    """
    row_id: str = ""
    mpn: str = ""
    brand_name: str = ""
    manufacturer_name: str = ""
    overall_confidence: float = 1.0
    defect_probability_index: float = 0.0
    risk_tier: str = "LOW"                 # LOW, ELEVATED, CRITICAL
    total_attributes_tracked: int = 0
    cached_attributes_count: int = 0
    uncached_attributes_count: int = 0
    cache_coverage_ratio: float = 0.0      # 0.0 to 1.0
    needs_hitl_review: bool = False
    verified_oem_sources_count: int = 0
    provenance_cells: Dict[str, CellProvenance] = Field(default_factory=dict)
    lineage_hash: str = ""
