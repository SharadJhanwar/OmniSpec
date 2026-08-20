import time
from compiler import OfflineParametricCompiler

TEST_QUERIES = [
    "Dishwasher under 45 dBA stainless steel 120V 15A",
    "DEWALT Cordless sliding miter saw with brushless motor under 35 lbs",
    "4-1/2 in metal cut off disc with 7/8 in arbor rated over 10000 RPM",
    "9.5W A19 LED light bulb 2700K medium E26 base",
    "3/8 in brass pipe coupling 150# NPT female",
    "Angle grinder 11000 RPM 7/8 in arbor 120V",
    "Whirlpool dishwasher stainless steel quiet under 42 dBA",
    "LED bulb 3000K warm white E26 base",
    "Milwaukee 5 in cut off wheel 7/8 arbor",
    "Brass pipe fitting coupler 150 lb class"
]


def run_compiler_benchmark():
    print("=" * 65)
    print("[BENCHMARK] NATURAL LANGUAGE -> PARAMETRIC AST COMPILER")
    print("=" * 65)

    total_time = 0.0
    successful_parses = 0

    for i, q in enumerate(TEST_QUERIES, 1):
        ast = OfflineParametricCompiler.parse_query(q)
        total_time += ast["parsing_latency_ms"]

        num_count = len(ast["numerical_constraints"])
        cat_count = len(ast["categorical_constraints"])
        has_category = bool(ast["category_intent"])

        if has_category and (num_count > 0 or cat_count > 0):
            successful_parses += 1

        print(f"\nQuery {i}: \"{q}\"")
        print(f"  * Category Intent: {ast['category_intent'] or 'Generic'}")
        print(f"  * Numerical Constraints : {num_count} -> {ast['numerical_constraints']}")
        print(f"  * Categorical Filters   : {cat_count} -> {ast['categorical_constraints']}")
        print(f"  * Compiled SQL          : {ast['compiled_sql']}")
        print(f"  * Parsing Latency       : {ast['parsing_latency_ms']:.3f} ms")

    avg_latency = total_time / len(TEST_QUERIES)
    accuracy = (successful_parses / len(TEST_QUERIES)) * 100

    print("\n" + "=" * 65)
    print(f"[SUMMARY] Total Queries: {len(TEST_QUERIES)} | Success Rate: {accuracy:.1f}%")
    print(f"[LATENCY] Average Parsing Latency: {avg_latency:.3f} ms / query (Deterministic Fast-Path)")
    print("=" * 65)


if __name__ == "__main__":
    run_compiler_benchmark()
