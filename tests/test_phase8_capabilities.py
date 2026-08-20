import pytest
from backend.app.services.parametric_search_engine import ParametricSearchEngine
from backend.app.schemas.search_schema import ParametricAST, SearchCandidateResult


def test_task22_ast_compilation_deterministic():
    """
    Test Task 22: Natural Language -> Parametric Abstract Syntax Tree (AST) compilation.
    """
    # 1. Multi-variable Appliance Query
    query_1 = "Dishwasher under 45 dBA stainless steel 120V 15A"
    ast_1 = ParametricSearchEngine.compile_query_to_ast(query_1)

    assert "Dishwashers" in ast_1.category_intent
    assert len(ast_1.numerical_constraints) == 2
    assert any(n.field == "Sound Level" and n.operator == "<=" and n.value == 45.0 for n in ast_1.numerical_constraints)
    assert any(n.field == "Amperage" and n.value == 15.0 for n in ast_1.numerical_constraints)
    assert any(c.field == "Finish" and "Stainless" in c.value for c in ast_1.categorical_constraints)
    assert "WHERE" in ast_1.compiled_sql
    assert ast_1.parser_used == "DETERMINISTIC_REGEX"

    # 2. Power Tool & Battery Platform Query
    query_2 = "DEWALT Cordless sliding miter saw with brushless motor under 35 lbs"
    ast_2 = ParametricSearchEngine.compile_query_to_ast(query_2)

    assert "Saws" in ast_2.category_intent
    assert any(n.field == "Weight" and n.value == 35.0 for n in ast_2.numerical_constraints)
    assert any(c.field == "Motor Type" and c.value == "Brushless" for c in ast_2.categorical_constraints)
    assert any(c.field == "Power Source" and c.value == "Cordless" for c in ast_2.categorical_constraints)

    # 3. Abrasive Cut-Off Wheel Query
    query_3 = "4-1/2 in metal cut off disc with 7/8 in arbor rated over 10000 RPM"
    ast_3 = ParametricSearchEngine.compile_query_to_ast(query_3)

    assert "Cut-Off Wheels" in ast_3.category_intent
    assert any(n.field == "Max RPM" and n.operator == ">=" and n.value == 10000.0 for n in ast_3.numerical_constraints)
    assert any(c.field == "Arbor Hole Size" and "7/8" in c.value for c in ast_3.categorical_constraints)


def test_task23_disqualification_and_tradeoff_explainer():
    """
    Test Task 23: Multi-variable constraint evaluation and delta explanations.
    """
    query = "Dishwasher under 45 dBA stainless steel 120V"
    ast = ParametricSearchEngine.compile_query_to_ast(query)

    # Product A: Bosch 42 dBA (Qualified - 100% Match)
    product_bosch = {
        "Mfg_Part_Num": "SHX78B75UC",
        "BRAND_NAME": "Bosch®",
        "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
        "SHORT_DESC": "Bosch® 800 Series 24 in Built-In Dishwasher Stainless Steel 42 dBA 120V",
        "Part_Desc": "Bosch 800 Series Dishwasher 42 dBA Stainless Steel 120V"
    }

    res_bosch = ParametricSearchEngine.evaluate_candidate(product_bosch, ast)
    assert res_bosch.match_status == "QUALIFIED"
    assert res_bosch.alignment_score == 1.0
    assert len(res_bosch.disqualification_reasons) == 0
    assert any("42.0 dBA meets constraint" in m for m in res_bosch.matched_constraints)

    # Product B: Frigidaire 47 dBA (Disqualified due to +2 dBA sound limit violation)
    product_frig = {
        "Mfg_Part_Num": "PDSH4816AF",
        "BRAND_NAME": "FRIGIDAIRE®",
        "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
        "SHORT_DESC": "FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher Stainless Steel 47 dBA 120V",
        "Part_Desc": "PDSH4816AF Dishwasher SS 47dBA 120V"
    }

    res_frig = ParametricSearchEngine.evaluate_candidate(product_frig, ast)
    assert res_frig.match_status == "DISQUALIFIED"
    assert len(res_frig.disqualification_reasons) > 0
    # Must explicitly state the numerical delta (+2.0 dBA)
    assert any("+2.0 dBA" in r for r in res_frig.disqualification_reasons)


def test_task23_end_to_end_parametric_search():
    """
    Test End-to-End Parametric Search Execution across catalog items.
    """
    catalog = [
        {
            "Mfg_Part_Num": "SHX78B75UC",
            "BRAND_NAME": "Bosch®",
            "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
            "SHORT_DESC": "Bosch® 800 Series Dishwasher Stainless Steel 42 dBA 120V",
            "Part_Desc": "Bosch Dishwasher 42 dBA Stainless Steel 120V"
        },
        {
            "Mfg_Part_Num": "PDSH4816AF",
            "BRAND_NAME": "FRIGIDAIRE®",
            "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
            "SHORT_DESC": "FRIGIDAIRE® Dishwasher Stainless Steel 47 dBA 120V",
            "Part_Desc": "Frigidaire Dishwasher 47 dBA Stainless Steel 120V"
        },
        {
            "Mfg_Part_Num": "DCS361B",
            "BRAND_NAME": "DEWALT®",
            "Classpath": "Tools & Instruments>Power Tools>Saws & Blades>Circular & Miter Saws",
            "SHORT_DESC": "DEWALT® 20V MAX Miter Saw Brushless Cordless",
            "Part_Desc": "DEWALT Saw 20V Cordless Brushless"
        }
    ]

    resp = ParametricSearchEngine.execute_search("Dishwasher under 45 dBA stainless steel 120V", catalog)

    assert resp.qualified_count == 1
    assert resp.qualified_matches[0].mpn == "SHX78B75UC"
    assert resp.disqualified_count >= 1
    assert any(d.mpn == "PDSH4816AF" for d in resp.disqualified_tradeoffs)
