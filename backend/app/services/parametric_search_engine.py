import re
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from ..schemas.search_schema import (
    NumericalConstraint,
    CategoricalConstraint,
    ParametricAST,
    SearchCandidateResult,
    ParametricSearchResponse
)
from ..core.config import settings


class ParametricSearchEngine:
    """
    Parametric Engineering Constraint Compiler & Disqualification Explainer Engine.
    Executes sub-millisecond AST extraction and multi-variable trade-off analysis over 252-column master catalog data.
    """

    CATEGORIES = {
        "dishwash": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
        "washer": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
        "saw": "Tools & Instruments>Power Tools>Saws & Blades>Circular & Miter Saws",
        "miter": "Tools & Instruments>Power Tools>Saws & Blades>Circular & Miter Saws",
        "grind": "Tools & Instruments>Power Tools>Grinders>Angle Grinders",
        "drill": "Tools & Instruments>Power Tools>Drills>Cordless Drills",
        "cut off": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels",
        "cut-off": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels",
        "disc": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels",
        "bulb": "Lighting & Electrical>Light Bulbs & Lamps>LED Light Bulbs",
        "lamp": "Lighting & Electrical>Light Bulbs & Lamps>LED Light Bulbs",
        "led": "Lighting & Electrical>Light Bulbs & Lamps>LED Light Bulbs",
        "deck": "Building Materials>Decking & Railing>Decking Boards",
        "cplg": "Plumbing & Pumps>Pipe Fittings>Couplings",
        "coupl": "Plumbing & Pumps>Pipe Fittings>Couplings",
        "fitting": "Plumbing & Pumps>Pipe Fittings>Couplings"
    }

    @classmethod
    def compile_query_to_ast(cls, query: str, enable_llm: bool = False) -> ParametricAST:
        """
        Compiles a natural language contractor query into a structured AST.
        """
        start_time = time.perf_counter()
        q_lower = query.lower()

        # Generative Fallback for ambiguous phrasing if explicitly requested and key available
        if enable_llm and settings.OPENAI_API_KEY and len(query.split()) > 7:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                prompt = (
                    f"Extract parametric constraints from this industrial query: '{query}'. "
                    f"Return JSON with: category_intent (string), numerical_constraints (list of {{field, operator, value, unit}}), "
                    f"categorical_constraints (list of {{field, operator, value}})."
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                data = json.loads(resp.choices[0].message.content)
                latency = round((time.perf_counter() - start_time) * 1000, 2)
                return ParametricAST(
                    raw_query=query,
                    category_intent=data.get("category_intent", ""),
                    numerical_constraints=[NumericalConstraint(**c) for c in data.get("numerical_constraints", [])],
                    categorical_constraints=[CategoricalConstraint(**c) for c in data.get("categorical_constraints", [])],
                    parser_used="GPT4O_MINI_GENERATIVE",
                    parsing_latency_ms=latency
                )
            except Exception as e:
                pass  # Fall back to deterministic regex parser

        # Deterministic Fast-Path Parser
        category_intent = ""
        for token, cat_path in cls.CATEGORIES.items():
            if token in q_lower:
                category_intent = cat_path
                break

        numerical_constraints = []
        categorical_constraints = []

        # 1. Sound Level (dBA)
        sound_match = re.search(r'(?:under|max|less than|<=|<)?\s*(\d+(?:\.\d+)?)\s*(?:dba|db|decibel)', q_lower)
        if sound_match:
            val = float(sound_match.group(1))
            op = "<=" if any(w in q_lower for w in ["under", "max", "less", "<", "<="]) else "=="
            numerical_constraints.append(NumericalConstraint(field="Sound Level", operator=op, value=val, unit="dBA"))

        # 2. Voltage (V)
        volt_match = re.search(r'(\d+)\s*(?:v|volt|volts)\b', q_lower)
        if volt_match:
            categorical_constraints.append(CategoricalConstraint(field="Voltage", operator="CONTAINS", value=f"{volt_match.group(1)} V"))

        # 3. Amperage (A)
        amp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:a|amp|amps)\b', q_lower)
        if amp_match:
            numerical_constraints.append(NumericalConstraint(field="Amperage", operator="==", value=float(amp_match.group(1)), unit="A"))

        # 4. RPM
        rpm_match = re.search(r'(?:over|min|at least|>=|>)?\s*(\d{4,5})\s*(?:rpm)', q_lower)
        if rpm_match:
            val = float(rpm_match.group(1))
            op = ">=" if any(w in q_lower for w in ["over", "min", "at least", ">", ">="]) else "=="
            numerical_constraints.append(NumericalConstraint(field="Max RPM", operator=op, value=val, unit="RPM"))

        # 5. Arbor Hole Size
        arbor_match = re.search(r'(\d+/\d+|\.\d+)\s*(?:in|inch|\"|\')?\s*arbor', q_lower)
        if arbor_match:
            categorical_constraints.append(CategoricalConstraint(field="Arbor Hole Size", operator="CONTAINS", value=arbor_match.group(1)))

        # 6. Diameter
        diam_match = re.search(r'(\d+(?:-\d+/\d+|\.\d+)?)\s*(?:in|inch|\"|\')?\s*(?:diam|disc|wheel|saw|blade)', q_lower)
        if diam_match:
            categorical_constraints.append(CategoricalConstraint(field="Diameter", operator="CONTAINS", value=diam_match.group(1)))

        # 7. Weight
        weight_match = re.search(r'(?:under|less than|max|<=|<)\s*(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound|pounds|kg)', q_lower)
        if weight_match:
            numerical_constraints.append(NumericalConstraint(field="Weight", operator="<=", value=float(weight_match.group(1)), unit="lbs"))

        # 8. Pressure Class
        pressure_match = re.search(r'(?:class\s*)?(\d{3})\s*(?:#|lb|psi)', q_lower)
        if pressure_match:
            categorical_constraints.append(CategoricalConstraint(field="Pressure Class", operator="CONTAINS", value=f"{pressure_match.group(1)} lb"))

        # 9. Lighting Color Temperature
        cct_match = re.search(r'(\d{4})\s*k\b', q_lower)
        if cct_match:
            categorical_constraints.append(CategoricalConstraint(field="Color Temperature", operator="CONTAINS", value=f"{cct_match.group(1)} K"))

        # 10. Socket Base
        if "e26" in q_lower or "medium base" in q_lower:
            categorical_constraints.append(CategoricalConstraint(field="Bulb Base Type", operator="CONTAINS", value="Medium E26"))
        elif "e12" in q_lower or "candelabra" in q_lower:
            categorical_constraints.append(CategoricalConstraint(field="Bulb Base Type", operator="CONTAINS", value="Candelabra E12"))

        # 11. Material & Finish
        if "stainless" in q_lower or " ss " in f" {q_lower} ":
            categorical_constraints.append(CategoricalConstraint(field="Finish", operator="CONTAINS", value="Stainless Steel"))
        if "brass" in q_lower:
            categorical_constraints.append(CategoricalConstraint(field="Material", operator="CONTAINS", value="Brass"))
        if "brushless" in q_lower:
            categorical_constraints.append(CategoricalConstraint(field="Motor Type", operator="CONTAINS", value="Brushless"))
        if "cordless" in q_lower:
            categorical_constraints.append(CategoricalConstraint(field="Power Source", operator="CONTAINS", value="Cordless"))

        # Compile SQL WHERE expression for DuckDB
        sql_clauses = []
        if category_intent:
            sql_clauses.append(f"UPPER(Classpath) LIKE '%{category_intent.split('>')[-1].upper()}%'")
        for num in numerical_constraints:
            sql_clauses.append(f"TRY_CAST({num.field.replace(' ', '_')} AS FLOAT) {num.operator} {num.value}")
        for cat in categorical_constraints:
            sql_clauses.append(f"UPPER({cat.field.replace(' ', '_')}) LIKE '%{cat.value.upper()}%'")

        compiled_sql = "SELECT * FROM catalog_delivery_252"
        if sql_clauses:
            compiled_sql += " WHERE " + " AND ".join(sql_clauses)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 3)

        return ParametricAST(
            raw_query=query,
            category_intent=category_intent,
            numerical_constraints=numerical_constraints,
            categorical_constraints=categorical_constraints,
            keyword_terms=[],
            compiled_sql=compiled_sql,
            parser_used="DETERMINISTIC_REGEX",
            parsing_latency_ms=latency_ms
        )

    @classmethod
    def evaluate_candidate(cls, item: Dict[str, Any], ast: ParametricAST) -> SearchCandidateResult:
        """
        Evaluates an individual catalog item against all compiled AST constraints,
        computing exact numerical deltas for any failing criteria.
        """
        matched: List[str] = []
        disqualified: List[str] = []

        desc = str(item.get("Part_Desc", "") or item.get("SHORT_DESC", "") or item.get("raw_part_desc", "")).lower()
        classpath = str(item.get("Classpath", "") or item.get("classpath", "")).lower()
        mpn = item.get("Mfg_Part_Num", "") or item.get("mfg_part_num", "") or item.get("clean_mfg_part_num", "") or "UNKNOWN"
        brand = item.get("BRAND_NAME", "") or item.get("brand_name", "") or "Brand"

        # 1. Category Alignment Check
        if ast.category_intent:
            cat_leaf = ast.category_intent.split(">")[-1].lower()
            if cat_leaf in classpath or cat_leaf in desc or any(t in desc for t in cat_leaf.split()):
                matched.append(f"Category Match: {ast.category_intent.split('>')[-1]}")
            else:
                disqualified.append(f"Category mismatch: Target is '{ast.category_intent.split('>')[-1]}' (Found: '{item.get('Classpath', 'Other')}')")

        # 2. Numerical Constraints (Sound Level, RPM, Weight, Amperage)
        for num in ast.numerical_constraints:
            field = num.field
            target_val = num.value
            op = num.operator

            # Extract actual numeric value from description or item attributes
            actual_val = None
            if field == "Sound Level":
                match = re.search(r'(\d+)\s*(?:dba|db)', desc)
                if match:
                    actual_val = float(match.group(1))
            elif field == "Max RPM":
                match = re.search(r'(\d{4,5})\s*rpm', desc)
                if match:
                    actual_val = float(match.group(1))
            elif field == "Amperage":
                match = re.search(r'(\d+(?:\.\d+)?)\s*(?:a|amp)', desc)
                if match:
                    actual_val = float(match.group(1))
            elif field == "Weight":
                match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lb|lbs)', desc)
                if match:
                    actual_val = float(match.group(1))

            if actual_val is not None:
                passed = False
                if op == "<=" and actual_val <= target_val:
                    passed = True
                elif op == ">=" and actual_val >= target_val:
                    passed = True
                elif op == "<" and actual_val < target_val:
                    passed = True
                elif op == ">" and actual_val > target_val:
                    passed = True
                elif op == "==" and abs(actual_val - target_val) < 0.1:
                    passed = True

                if passed:
                    matched.append(f"✓ {field} {actual_val} {num.unit} meets constraint ({op} {target_val} {num.unit})")
                else:
                    delta = actual_val - target_val
                    sign = "+" if delta > 0 else ""
                    disqualified.append(f"❌ Failed Constraint [{field}]: Actual value is {actual_val} {num.unit} ({sign}{delta:.1f} {num.unit} outside {op} {target_val} {num.unit} limit)")
            else:
                # Value not specified in descriptor
                disqualified.append(f"⚠️ Unspecified [{field}]: Specification not explicitly confirmed in product data")

        # 3. Categorical Constraints (Finish, Voltage, Arbor, Base Type, Material)
        for cat in ast.categorical_constraints:
            field = cat.field
            target_str = cat.value.lower()

            if cat.field == "Voltage":
                v_match = re.search(r'(\d+v)', desc)
                if v_match and v_match.group(1) in target_str.replace(" ", ""):
                    matched.append(f"✓ Voltage: {v_match.group(1).upper()} verified")
                elif v_match:
                    disqualified.append(f"❌ Voltage Conflict: Required {cat.value} but product is rated {v_match.group(1).upper()}")
                elif target_str in desc:
                    matched.append(f"✓ Voltage: {cat.value} verified")
                else:
                    disqualified.append(f"⚠️ Voltage Unverified: {cat.value} not confirmed")
            elif cat.field == "Arbor Hole Size":
                if "7/8" in target_str and ("7/8" in desc or "7/8 in" in desc):
                    matched.append(f"✓ Arbor Hole: 7/8 in verified")
                elif "5/8" in desc and "7/8" in target_str:
                    disqualified.append(f"❌ Arbor Hole Mismatch: Required 7/8 in but product arbor is 5/8 in")
                elif target_str in desc:
                    matched.append(f"✓ Arbor Hole: {cat.value} verified")
                else:
                    disqualified.append(f"⚠️ Arbor Hole Unverified: {cat.value} not confirmed")
            else:
                if target_str in desc:
                    matched.append(f"✓ {field}: {cat.value} verified")
                else:
                    disqualified.append(f"❌ Missing Spec [{field}]: Expected '{cat.value}' not found in record")

        # Overall Qualification
        total_checks = len(ast.numerical_constraints) + len(ast.categorical_constraints) + (1 if ast.category_intent else 0)
        passed_count = len(matched)

        is_qualified = (len(disqualified) == 0) and (passed_count > 0 or total_checks == 0)
        alignment_score = round(passed_count / max(1, total_checks), 2) if total_checks > 0 else 1.0

        return SearchCandidateResult(
            mpn=mpn,
            brand_name=brand,
            manufacturer_name=item.get("MANUFACTURER_NAME", "") or item.get("manufacturer_name", ""),
            short_desc=item.get("SHORT_DESC", "") or item.get("Part_Desc", ""),
            classpath=item.get("Classpath", "") or item.get("classpath", "Industrial Standard"),
            match_status="QUALIFIED" if is_qualified else "DISQUALIFIED",
            alignment_score=alignment_score,
            matched_constraints=matched,
            disqualification_reasons=disqualified,
            extracted_specs={"raw_desc": desc}
        )

    @classmethod
    def execute_search(
        cls,
        query: str,
        catalog_items: List[Dict[str, Any]],
        enable_llm: bool = False
    ) -> ParametricSearchResponse:
        """
        Full pipeline: NL -> AST -> Candidate Evaluation -> Qualified & Trade-Off Sets.
        """
        start_time = time.perf_counter()
        ast = cls.compile_query_to_ast(query, enable_llm=enable_llm)

        qualified: List[SearchCandidateResult] = []
        disqualified: List[SearchCandidateResult] = []

        for item in catalog_items:
            res = cls.evaluate_candidate(item, ast)
            if res.match_status == "QUALIFIED":
                qualified.append(res)
            else:
                # Only include disqualified items that had at least one partial relevance match
                if res.alignment_score > 0.0 or any(kw in res.short_desc.lower() for kw in query.lower().split()[:2]):
                    disqualified.append(res)

        # Sort qualified by highest alignment descending
        qualified.sort(key=lambda x: x.alignment_score, reverse=True)
        # Sort disqualified by highest partial alignment descending (near-misses first)
        disqualified.sort(key=lambda x: x.alignment_score, reverse=True)

        exec_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return ParametricSearchResponse(
            ast=ast,
            total_candidates_scanned=len(catalog_items),
            qualified_count=len(qualified),
            disqualified_count=len(disqualified),
            qualified_matches=qualified,
            disqualified_tradeoffs=disqualified[:8],  # Top 8 near-miss trade-offs
            execution_time_ms=exec_ms
        )
