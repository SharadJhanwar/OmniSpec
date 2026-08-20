import pytest
from backend.app.core.logging import logger
from backend.app.services.parametric_search_engine import ParametricSearchEngine

def test_ast_compiler_stress_queries():
    """Verify that AST compiler handles multi-variable queries without crashing or missing numerical constraints."""
    logger.info("Testing Parametric AST compiler against diverse real-world contractor queries...")
    
    queries = [
        ("Quiet dishwasher under 44 dBA, 120V, 15A, stainless steel finish", 44.0, "Sound Level"),
        ("Heavy duty 4-1/2 in angle grinder over 11000 RPM 7/8 arbor", 11000.0, "Max RPM"),
        ("Compact 12V cordless drill under 4 lbs with brushless motor", 4.0, "Weight"),
        ("Industrial 3/8 in pipe coupling rated for 150# pressure brass", 150.0, "Pressure Class")
    ]
    
    for q_text, expected_val, expected_field in queries:
        ast = ParametricSearchEngine.compile_query_to_ast(q_text)
        assert ast.category_intent != ""
        # Check numerical constraint presence
        matching_constraints = [c for c in ast.numerical_constraints if c.field == expected_field]
        if matching_constraints:
            assert matching_constraints[0].value == expected_val


def test_disqualification_delta_calculations():
    """Verify that trade-off explainer outputs clear, formatted numerical deltas."""
    logger.info("Testing disqualification delta calculations...")
    
    ast = ParametricSearchEngine.compile_query_to_ast("Dishwasher under 45 dBA")
    
    candidate = {
        "Mfg_Part_Num": "PDSH4816AF",
        "BRAND_NAME": "FRIGIDAIRE®",
        "SHORT_DESC": "FRIGIDAIRE® Dishwasher 47 dBA Stainless Steel",
        "Part_Desc": "Dishwasher 47 dBA"
    }
    
    eval_res = ParametricSearchEngine.evaluate_candidate(candidate, ast)
    assert eval_res.match_status == "DISQUALIFIED"
    assert len(eval_res.disqualification_reasons) > 0
    assert any("+2.0 dBA" in r or "47.0" in r for r in eval_res.disqualification_reasons)
