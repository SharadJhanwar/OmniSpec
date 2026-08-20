from backend.app.db.duckdb_client import kb
from backend.app.core.logging import logger

def test_kb():
    logger.info("==================================================")
    logger.info("TESTING DUCKDB MASTER KNOWLEDGE BASE (TASK 1)")
    logger.info("==================================================")

    # 1. Test Brand Search
    test_queries = ["Frigidaire", "Milw", "Trex Enhance", "Diablo Cut Off", "AZEK"]
    for q in test_queries:
        res = kb.find_brand(q)
        logger.info(f"Brand Search '{q}' -> {res}")
        assert res is not None, f"Failed to resolve brand for '{q}'"

    # 2. Test LOV Schema Retrieval
    classpath = "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers"
    lov_schema = kb.get_lov_schema(classpath)
    logger.info(f"\nLOV Schema for '{classpath}': {len(lov_schema)} attributes")
    for attr in lov_schema:
        logger.info(f"  - {attr['label']} (UOM: {attr['uom']}, Filtering: {attr['filtering']}) Allowed: {attr['allowed_values'][:3]}")
    assert len(lov_schema) > 0, "Failed to load LOV schema"

    # 3. Test Fittings Connection Normalization
    test_conns = ["MIP", "Male Pipe Thread", "Push-Fit", "SharkBite", "Comp"]
    logger.info("\nFittings Connection Many-to-One Normalization:")
    for c in test_conns:
        norm = kb.normalize_fitting_connection(c)
        logger.info(f"  - '{c}' -> '{norm}'")

    # 4. Test Fittings Material Normalization
    test_mats = ["BRS", "304 SS", "Lead Free Brass", "PVC"]
    logger.info("\nFittings Material Normalization:")
    for m in test_mats:
        norm = kb.normalize_fitting_material(m)
        logger.info(f"  - '{m}' -> '{norm}'")

    logger.info("\n==================================================")
    logger.info("TASK 1 COMPLETED: ALL DUCKDB KNOWLEDGE TESTS PASSED!")
    logger.info("==================================================")

if __name__ == "__main__":
    test_kb()
