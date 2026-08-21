from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .delivery_schema import DeliveryProductRecord


class AgentTrace(BaseModel):
    agent_name: str
    status: str = "COMPLETED"  # RUNNING, COMPLETED, FAILED, SKIPPED
    execution_time_ms: float = 0.0
    notes: List[str] = Field(default_factory=list)
    extracted_data: Dict[str, Any] = Field(default_factory=dict)


class ProductEnrichmentState(BaseModel):
    """
    Master State passed sequentially through the 9-Agent LangGraph Swarm
    """
    # Raw Ingested Row
    row_id: str = ""
    raw_mfg_part_num: str = ""
    raw_part_desc: str = ""
    raw_e1_brand: str = ""
    raw_unilog_brand: str = ""
    raw_dib_brand: str = ""
    raw_part_manuf: str = ""
    raw_sku: str = ""
    raw_dept: str = ""
    raw_class: str = ""
    raw_fine: str = ""
    enable_llm: bool = False
    is_cached: bool = False
    cache_source: str = ""  # 'human_override', 'master_kb', 'unassigned'

    # Agent 1: De-noised & Tokenized
    clean_mfg_part_num: str = ""
    cleaned_part_desc: str = ""
    clean_supplier_name: str = ""
    supplier_vendor_code: str = ""
    token_bag: Dict[str, Any] = Field(default_factory=dict)

    # Agent 2: Brand & Entity Resolution
    manufacturer_name: str = ""
    brand_name: str = ""
    trade_name: str = ""
    mfr_part_number: str = ""
    alt_part_number: str = ""
    brand_confidence: float = 1.0

    # Agent 3: Taxonomy & UNSPSC
    classpath: str = ""
    dept: str = ""
    class_name: str = ""
    fine: str = ""
    product_name: str = ""
    unspsc: str = ""
    taxonomy_confidence: float = 1.0

    # Agent 4: Spec, Dimension & UOM
    dimensions: Dict[str, str] = Field(default_factory=dict)
    electrical_specs: Dict[str, str] = Field(default_factory=dict)
    acoustic_specs: Dict[str, str] = Field(default_factory=dict)
    packaging_specs: Dict[str, str] = Field(default_factory=dict)
    spec_confidence: float = 1.0

    # Agent 5: OEM Sourcing & RAG
    mfr_url: str = ""
    ref_urls: List[str] = Field(default_factory=list)
    standard_approvals: str = ""
    sourcing_confidence: float = 1.0

    # Agent 6: Constrained LOV Attributes (50 Triples = 150 Columns)
    attributes: Dict[str, str] = Field(default_factory=dict)
    with_features: str = ""
    includes: str = ""
    application: str = ""
    prop_65: str = ""
    warranty: str = ""
    lov_compliance_score: float = 1.0

    # Agent 7: Multi-Channel Copy
    invoice_desc: str = ""
    mobile_desc: str = ""
    short_desc: str = ""
    long_desc1: str = ""
    retail_desc: str = ""
    marketing_desc: str = ""
    item_features: List[str] = Field(default_factory=list)

    # Agent 8: Digital Assets
    digital_assets: Dict[str, str] = Field(default_factory=dict)

    # Agent 9: Quality & HITL
    overall_confidence: float = 1.0
    integrity_violations: List[str] = Field(default_factory=list)
    provenance_map: Dict[str, Any] = Field(default_factory=dict)
    needs_hitl_review: bool = False
    hitl_reason: str = ""

    # Execution Trace & 252-Col Delivery Format
    traces: List[AgentTrace] = Field(default_factory=list)
    delivery_record: Optional[DeliveryProductRecord] = None
