from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class VariantAxis(BaseModel):
    """Represents a dimension of product variation (e.g. Configuration, Finish, Size)"""
    name: str
    values: List[str] = Field(default_factory=list)


class ChildVariant(BaseModel):
    """Represents an individual SKU variant belonging to a parent product family"""
    mpn: str
    brand_name: str
    manufacturer_name: str = ""
    short_desc: str
    axis_values: Dict[str, str] = Field(default_factory=dict)
    spec_highlights: Dict[str, str] = Field(default_factory=dict)
    image_url: str = ""


class AssortmentGap(BaseModel):
    """Represents an evidence-backed missing dimensional sequence in a product family"""
    family_id: str
    family_name: str
    brand_name: str
    dimension_name: str
    present_sizes: List[str] = Field(default_factory=list)
    missing_sizes: List[str] = Field(default_factory=list)
    gap_severity: str = "HIGH"  # HIGH (high volume gap like 1/2 in) or MEDIUM
    confidence_level: str = "POTENTIAL_GAP_DETECTED"  # CONFIRMED_MANUFACTURER_GAP or POTENTIAL_GAP_DETECTED
    evidence_notes: str = ""


class ParentProductFamily(BaseModel):
    """Represents a discovered canonical Parent PDP grouping multiple variant SKUs"""
    family_id: str
    family_name: str
    brand_name: str
    category_path: str
    base_series_mpn: str
    total_variants: int = 0
    variant_axes: List[VariantAxis] = Field(default_factory=list)
    variants: List[ChildVariant] = Field(default_factory=list)
    detected_gaps: List[AssortmentGap] = Field(default_factory=list)


class FamilyDiscoveryResponse(BaseModel):
    """Response envelope for catalog-wide family discovery and gap detection"""
    total_families_discovered: int = 0
    total_child_skus_clustered: int = 0
    families: List[ParentProductFamily] = Field(default_factory=list)
    all_gaps: List[AssortmentGap] = Field(default_factory=list)
    execution_time_ms: float = 0.0
