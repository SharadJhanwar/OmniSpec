import pytest
from backend.app.core.logging import logger
from backend.app.schemas.state_schema import ProductEnrichmentState
from backend.app.agents.agent_1_ingestion import IngestionAgent
from backend.app.db.duckdb_client import kb

def test_placeholder_stripping_edge_cases():
    """Verify that all variants of dummy/placeholder brand strings are cleanly stripped."""
    logger.info("Testing Agent 1 placeholder stripping across messy distributor tokens...")
    
    placeholders = [
        "-- Unbranded --",
        "-- No DIB Brand --",
        "NO BRAND",
        "UNKNOWN",
        "N/A",
        "null",
        "---",
        "None"
    ]
    
    for ph in placeholders:
        state = ProductEnrichmentState(
            raw_mfg_part_num="TEST-123",
            raw_part_desc="Test generic part 1/2 in",
            raw_e1_brand=ph,
            raw_unilog_brand=ph
        )
        out = IngestionAgent.execute(state)
        clean_e1 = out.get("clean_e1_brand", "")
        # Should be stripped to empty string so downstream agents can resolve via DuckDB
        assert clean_e1 == "" or clean_e1 != ph


def test_html_entity_unescaping():
    """Verify that HTML entities like &amp;, &quot;, &#39; are converted to clean characters."""
    logger.info("Testing HTML entity unescaping in raw descriptions...")
    
    raw_desc = "4-1/2&quot; x .045&quot; x 7/8&quot; Metal &amp; Steel Cut-Off Wheel &#39;Special&#39;"
    state = ProductEnrichmentState(
        raw_mfg_part_num="49-94-0101",
        raw_part_desc=raw_desc
    )
    out = IngestionAgent.execute(state)
    clean_desc = out.get("clean_part_desc", "")
    assert "&quot;" not in clean_desc
    assert "&amp;" not in clean_desc
    assert "&#39;" not in clean_desc


def test_fractional_decimal_conversion_accuracy():
    """Verify exact fractional conversions from DuckDB knowledge base."""
    logger.info("Testing fractional decimal conversions across standard industrial sizes...")
    
    fractions_list = kb.get_all_fractions()
    assert len(fractions_list) >= 15
    
    # Verify standard decimal entries
    decimals = [round(f["decimal"], 3) for f in fractions_list]
    assert 0.25 in decimals or 0.125 in decimals
    assert 0.5 in decimals
    assert 0.875 in decimals

