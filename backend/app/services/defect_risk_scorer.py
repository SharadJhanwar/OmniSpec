from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field
from ..schemas.state_schema import ProductEnrichmentState


class RiskEvaluationResult(BaseModel):
    dpi_score: float = 0.0               # Defect Probability Index [0.0 - 1.0]
    risk_tier: str = "LOW"               # LOW, ELEVATED, CRITICAL
    recommended_action: str = "AUTO_APPROVE"  # AUTO_APPROVE, SECONDARY_AUDIT, IMMEDIATE_HITL_REQUIRED
    top_risk_factors: List[str] = Field(default_factory=list)
    component_scores: Dict[str, float] = Field(default_factory=dict)


class DefectRiskScorer:
    """
    Defect Probability Index (DPI) & Risk Queue Engine
    Evaluates multi-dimensional risk signals across brand confidence, schema violations,
    character bounds, and token entropy to rank review queues.
    """

    @classmethod
    def evaluate_risk(cls, state: ProductEnrichmentState) -> RiskEvaluationResult:
        factors: List[Tuple[float, str]] = []
        components: Dict[str, float] = {}

        # 1. Brand Risk (Weight: 0.30)
        brand_conf_delta = max(0.0, 1.0 - state.brand_confidence)
        has_symbol = bool("®" in state.brand_name or "™" in state.brand_name)
        brand_symbol_penalty = 0.0 if has_symbol else 0.35
        brand_score = min(1.0, (brand_conf_delta * 0.7) + (brand_symbol_penalty * 0.3))
        components["brand_risk"] = round(brand_score, 3)

        if brand_conf_delta > 0.15:
            factors.append((brand_conf_delta * 0.30, f"Low brand match confidence ({int(state.brand_confidence * 100)}%)"))
        if not has_symbol and state.brand_name:
            factors.append((0.15, "Missing mandatory registered trademark mark (®/™)"))

        # 2. Copy Bounds & Character Caps (Weight: 0.25)
        copy_penalty = 0.0
        inv_len = len(state.invoice_desc) if state.invoice_desc else 0
        mob_len = len(state.mobile_desc) if state.mobile_desc else 0

        if inv_len > 40:
            overflow = inv_len - 40
            inv_pen = min(1.0, 0.5 + (overflow * 0.05))
            copy_penalty += inv_pen * 0.6
            factors.append((0.20, f"INVOICE_DESC exceeds 40-char limit ({inv_len} chars)"))
        elif inv_len == 0:
            copy_penalty += 0.5
            factors.append((0.15, "Missing INVOICE_DESC"))

        if mob_len > 0 and (mob_len < 60 or mob_len > 80):
            copy_penalty += 0.4
            factors.append((0.10, f"MOBILE_DESC outside 60-80 char target ({mob_len} chars)"))
        elif mob_len == 0:
            copy_penalty += 0.3
            factors.append((0.10, "Missing MOBILE_DESC"))

        copy_score = min(1.0, copy_penalty)
        components["copy_bounds_risk"] = round(copy_score, 3)

        # 3. Schema & Integrity Rule Violations (Weight: 0.25)
        schema_penalty = 0.0
        audit_notes = [note for trace in state.traces if trace.agent_name == "agent_9_quality_audit" for note in trace.notes]
        violation_count = len(state.integrity_violations) + sum(1 for note in audit_notes if "VIOLATION" in note or "FAIL" in note or "Warning" in note)
        
        if violation_count > 0:
            schema_penalty = min(1.0, violation_count * 0.25)
            factors.append((min(0.25, violation_count * 0.10), f"{violation_count} integrity audit rule warnings detected"))
        
        components["schema_violation_risk"] = round(schema_penalty, 3)

        # 4. Sourcing & Lineage Risk (Weight: 0.20)
        sourcing_delta = max(0.0, 1.0 - state.sourcing_confidence)
        if not state.mfr_url or "placeholder" in state.mfr_url.lower():
            sourcing_delta = max(sourcing_delta, 0.60)
            factors.append((0.15, "Unverified or missing OEM manufacturer URL"))
        
        components["sourcing_risk"] = round(sourcing_delta, 3)

        # Composite Defect Probability Index Calculation
        dpi = (
            brand_score * 0.30 +
            copy_score * 0.25 +
            schema_penalty * 0.25 +
            sourcing_delta * 0.20
        )
        dpi = max(0.0, min(1.0, dpi))

        # Risk Tier Classification
        if dpi >= 0.55:
            risk_tier = "CRITICAL"
            recommended_action = "IMMEDIATE_HITL_REQUIRED"
        elif dpi >= 0.25:
            risk_tier = "ELEVATED"
            recommended_action = "SECONDARY_AUDIT"
        else:
            risk_tier = "LOW"
            recommended_action = "AUTO_APPROVE"

        # Sort factors by highest impact descending
        factors.sort(key=lambda x: x[0], reverse=True)
        top_factor_strings = [f"{desc} (+{round(score * 100)}% risk)" for score, desc in factors[:4]]

        return RiskEvaluationResult(
            dpi_score=round(dpi, 3),
            risk_tier=risk_tier,
            recommended_action=recommended_action,
            top_risk_factors=top_factor_strings if top_factor_strings else ["All core integrity rules and brand validations passed"],
            component_scores=components
        )
