import time
import re
import hashlib
from typing import Dict, Any, List, Tuple
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..services.normalizer import IngestionNormalizer
from ..db.duckdb_client import kb
from ..core.logging import logger


class IngestionAgent:
    """
    Agent 1: Ingestion, De-Noising & Tokenizer Agent
    Eradicates placeholders, normalizes corrupted dimension strings,
    isolates vendor ERP codes, resolves trade jargon, and structures raw token bags.
    """

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        # 1. Clean and validate MPN
        clean_mpn = (state.raw_mfg_part_num or "").strip()

        # 2. Extract supplier name and vendor code
        clean_supp, vendor_code = IngestionNormalizer.extract_vendor_code(state.raw_part_manuf)

        # 3. Purge brand placeholders
        clean_e1 = IngestionNormalizer.clean_placeholder(state.raw_e1_brand)
        clean_unilog = IngestionNormalizer.clean_placeholder(state.raw_unilog_brand)
        clean_dib = IngestionNormalizer.clean_placeholder(state.raw_dib_brand)

        # 4. Clean description (strip duplicate MPN prefix, normalize quotes & hyphens)
        clean_desc = IngestionNormalizer.clean_description(state.raw_part_desc, clean_mpn)

        # 5. Extract structured dimension tokens
        dim_tokens = IngestionNormalizer.extract_dimension_triplets(clean_desc)

        # 6. Extract packaging / quantity tokens (e.g. '6pc', '10pc', '50 Disc/Box')
        pack_match = re.findall(r"\b(\d+\s*(?:pc|pk|pack|disc/box|count|ct))\b", clean_desc, flags=re.IGNORECASE)
        pack_qty = pack_match[0] if pack_match else ""

        # 7. Extract candidate brand keywords
        brand_candidates = []
        for cand in [clean_e1, clean_unilog, clean_dib, clean_supp]:
            if cand and cand not in brand_candidates:
                brand_candidates.append(cand)

        # 8. Check Trade Jargon & Slang Thesaurus (e.g. 'sawzall' -> Reciprocating Saw)
        thesaurus_match = kb.lookup_thesaurus(clean_desc)

        # Generate unique row fingerprint
        row_hash = hashlib.sha256(f"{clean_mpn}:{state.raw_part_desc}".encode("utf-8")).hexdigest()

        notes = [
            f"Row hash: {row_hash[:8]}",
            f"Extracted {len(dim_tokens)} dimension blocks",
            f"Supplier: '{clean_supp}' (Vendor Code: '{vendor_code}')"
        ]
        if thesaurus_match:
            notes.append(f"Trade Jargon mapped: '{thesaurus_match[0]}' ({thesaurus_match[1]})")

        trace = AgentTrace(
            agent_name="Agent 1: Ingestion & De-Noising",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=notes,
            extracted_data={
                "clean_mpn": clean_mpn,
                "clean_supplier": clean_supp,
                "vendor_code": vendor_code,
                "brand_candidates": brand_candidates,
                "dimensions": dim_tokens,
                "pack_qty": pack_qty,
                "thesaurus_canonical": thesaurus_match[0] if thesaurus_match else None,
                "thesaurus_category": thesaurus_match[1] if thesaurus_match else None
            }
        )

        return {
            "clean_mfg_part_num": clean_mpn,
            "cleaned_part_desc": clean_desc,
            "clean_supplier_name": clean_supp,
            "supplier_vendor_code": vendor_code,
            "token_bag": {
                "brand_candidates": brand_candidates,
                "dimensions": dim_tokens,
                "pack_qty": pack_qty,
                "thesaurus": thesaurus_match
            },
            "traces": [trace]
        }
