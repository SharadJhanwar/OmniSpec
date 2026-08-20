import re
import time
from typing import Dict, Any, List, Optional, Tuple


class OfflineParametricCompiler:
    """
    Offline Research Compiler: Natural Language Query -> Parametric Abstract Syntax Tree (AST).
    Uses deterministic tokenization, domain regex heuristics, and physical unit normalization.
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
    def parse_query(cls, query: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        q_lower = query.lower()

        # 1. Identify Category Intent
        category_intent = ""
        for token, cat_path in cls.CATEGORIES.items():
            if token in q_lower:
                category_intent = cat_path
                break

        numerical_constraints = []
        categorical_constraints = []
        keywords = []

        # 2. Sound Level (e.g., "under 45 dba", "max 44 dba", "< 47 dba")
        sound_match = re.search(r'(?:under|max|less than|<=|<)?\s*(\d+(?:\.\d+)?)\s*(?:dba|db|decibel)', q_lower)
        if sound_match:
            val = float(sound_match.group(1))
            op = "<=" if any(w in q_lower for w in ["under", "max", "less", "<", "<="]) else "=="
            numerical_constraints.append({
                "field": "Sound Level",
                "operator": op,
                "value": val,
                "unit": "dBA"
            })

        # 3. Voltage (e.g., "120v", "20v max", "18v", "240v")
        volt_match = re.search(r'(\d+)\s*(?:v|volt|volts)\b', q_lower)
        if volt_match:
            categorical_constraints.append({
                "field": "Voltage",
                "operator": "CONTAINS",
                "value": f"{volt_match.group(1)} V"
            })

        # 4. Amperage / Current (e.g., "15a", "10 amp", "15 amp")
        amp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:a|amp|amps)\b', q_lower)
        if amp_match:
            numerical_constraints.append({
                "field": "Amperage",
                "operator": "==",
                "value": float(amp_match.group(1)),
                "unit": "A"
            })

        # 5. RPM / Speed (e.g., "11000 rpm", "over 10000 rpm", "min 5000 rpm")
        rpm_match = re.search(r'(?:over|min|at least|>=|>)?\s*(\d{4,5})\s*(?:rpm)', q_lower)
        if rpm_match:
            val = float(rpm_match.group(1))
            op = ">=" if any(w in q_lower for w in ["over", "min", "at least", ">", ">="]) else "=="
            numerical_constraints.append({
                "field": "Max RPM",
                "operator": op,
                "value": val,
                "unit": "RPM"
            })

        # 6. Arbor Hole Size (e.g., "7/8 in arbor", "5/8 arbor", "1/4 arbor")
        arbor_match = re.search(r'(\d+/\d+|\.\d+)\s*(?:in|inch|\"|\')?\s*arbor', q_lower)
        if arbor_match:
            categorical_constraints.append({
                "field": "Arbor Hole Size",
                "operator": "CONTAINS",
                "value": arbor_match.group(1)
            })

        # 7. Wheel / Blade Diameter (e.g., "4-1/2 in", "7-1/4 in", "5 in")
        diam_match = re.search(r'(\d+(?:-\d+/\d+|\.\d+)?)\s*(?:in|inch|\"|\')?\s*(?:diam|disc|wheel|saw|blade)', q_lower)
        if diam_match:
            categorical_constraints.append({
                "field": "Diameter",
                "operator": "CONTAINS",
                "value": diam_match.group(1)
            })

        # 8. Weight Bounds (e.g., "under 6 lbs", "less than 35 lbs", "< 5 kg")
        weight_match = re.search(r'(?:under|less than|max|<=|<)\s*(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound|pounds|kg)', q_lower)
        if weight_match:
            numerical_constraints.append({
                "field": "Weight",
                "operator": "<=",
                "value": float(weight_match.group(1)),
                "unit": "lbs"
            })

        # 9. Pressure Class (e.g., "150#", "150 lb", "class 150")
        pressure_match = re.search(r'(?:class\s*)?(\d{3})\s*(?:#|lb|psi)', q_lower)
        if pressure_match:
            categorical_constraints.append({
                "field": "Pressure Class",
                "operator": "CONTAINS",
                "value": f"{pressure_match.group(1)} lb"
            })

        # 10. Lighting Color Temperature (e.g., "2700k", "3000k", "5000k")
        cct_match = re.search(r'(\d{4})\s*k\b', q_lower)
        if cct_match:
            categorical_constraints.append({
                "field": "Color Temperature",
                "operator": "CONTAINS",
                "value": f"{cct_match.group(1)} K"
            })

        # 11. Lighting Socket Base (e.g., "e26", "medium base", "e12", "candelabra")
        if "e26" in q_lower or "medium base" in q_lower:
            categorical_constraints.append({
                "field": "Bulb Base Type",
                "operator": "CONTAINS",
                "value": "Medium E26"
            })
        elif "e12" in q_lower or "candelabra" in q_lower:
            categorical_constraints.append({
                "field": "Bulb Base Type",
                "operator": "CONTAINS",
                "value": "Candelabra E12"
            })

        # 12. Material & Finish Filters (Stainless Steel, Brass, Brushless, Cordless)
        if "stainless" in q_lower or " ss " in f" {q_lower} ":
            categorical_constraints.append({"field": "Finish", "operator": "CONTAINS", "value": "Stainless Steel"})
        if "brass" in q_lower:
            categorical_constraints.append({"field": "Material", "operator": "CONTAINS", "value": "Brass"})
        if "brushless" in q_lower:
            categorical_constraints.append({"field": "Motor Type", "operator": "CONTAINS", "value": "Brushless"})
        if "cordless" in q_lower:
            categorical_constraints.append({"field": "Power Source", "operator": "CONTAINS", "value": "Cordless"})

        # Compile SQL WHERE expression for DuckDB
        sql_clauses = []
        if category_intent:
            sql_clauses.append(f"UPPER(Classpath) LIKE '%{category_intent.split('>')[-1].upper()}%'")
        for num in numerical_constraints:
            sql_clauses.append(f"TRY_CAST({num['field'].replace(' ', '_')} AS FLOAT) {num['operator']} {num['value']}")
        for cat in categorical_constraints:
            sql_clauses.append(f"UPPER({cat['field'].replace(' ', '_')}) LIKE '%{cat['value'].upper()}%'")

        compiled_sql = "SELECT * FROM catalog_delivery_252"
        if sql_clauses:
            compiled_sql += " WHERE " + " AND ".join(sql_clauses)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 3)

        return {
            "raw_query": query,
            "category_intent": category_intent,
            "numerical_constraints": numerical_constraints,
            "categorical_constraints": categorical_constraints,
            "keyword_terms": keywords,
            "compiled_sql": compiled_sql,
            "parser_used": "DETERMINISTIC_REGEX",
            "parsing_latency_ms": latency_ms
        }
