from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NumericalConstraint(BaseModel):
    """Represents a numeric boundary constraint (e.g., Sound Level <= 45 dBA, Weight < 6.0 lbs)"""
    field: str
    operator: str  # '<=', '>=', '<', '>', '==', 'BETWEEN'
    value: float
    value_high: Optional[float] = None
    unit: str = ""


class CategoricalConstraint(BaseModel):
    """Represents a categorical/textual constraint (e.g., Finish = 'Stainless Steel', Voltage = '120 V')"""
    field: str
    operator: str = "EQUALS"  # 'EQUALS', 'CONTAINS', 'NOT_EQUALS'
    value: str


class ParametricAST(BaseModel):
    """Abstract Syntax Tree representing the compiled natural language search query"""
    raw_query: str
    category_intent: str = ""
    numerical_constraints: List[NumericalConstraint] = Field(default_factory=list)
    categorical_constraints: List[CategoricalConstraint] = Field(default_factory=list)
    keyword_terms: List[str] = Field(default_factory=list)
    compiled_sql: str = ""
    parser_used: str = "DETERMINISTIC_REGEX"  # DETERMINISTIC_REGEX or GPT4O_MINI_GENERATIVE
    parsing_latency_ms: float = 0.0


class SearchCandidateResult(BaseModel):
    """Represents an evaluated candidate product with qualification or disqualification reasoning"""
    mpn: str
    brand_name: str
    manufacturer_name: str = ""
    short_desc: str
    classpath: str
    match_status: str = "QUALIFIED"  # QUALIFIED or DISQUALIFIED
    alignment_score: float = 1.0     # 0.0 to 1.0
    matched_constraints: List[str] = Field(default_factory=list)
    disqualification_reasons: List[str] = Field(default_factory=list)
    extracted_specs: Dict[str, str] = Field(default_factory=dict)


class ParametricSearchResponse(BaseModel):
    """API response envelope for parametric engineering search"""
    ast: ParametricAST
    total_candidates_scanned: int = 0
    qualified_count: int = 0
    disqualified_count: int = 0
    qualified_matches: List[SearchCandidateResult] = Field(default_factory=list)
    disqualified_tradeoffs: List[SearchCandidateResult] = Field(default_factory=list)
    execution_time_ms: float = 0.0
