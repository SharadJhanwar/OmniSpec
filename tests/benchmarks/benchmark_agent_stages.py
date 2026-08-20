import sys
import time
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.schemas.state_schema import ProductEnrichmentState
from app.agents.agent_1_ingestion import IngestionAgent
from app.agents.agent_2_entity_resolution import EntityResolutionAgent
from app.agents.agent_3_taxonomy import TaxonomyClassifierAgent
from app.agents.agent_4_spec_uom import SpecUOMExtractorAgent
from app.agents.agent_5_oem_sourcing import OEMSourcingRAGAgent
from app.agents.agent_6_lov_mapper import ConstrainedLOVMapperAgent
from app.agents.agent_7_copy_builder import MultiChannelCopyAgent
from app.agents.agent_8_digital_assets import DigitalAssetAgent
from app.agents.agent_9_quality_audit import QualityAuditAgent
from app.core.logging import logger

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_stage_banner(stage_num: int, stage_name: str, agent_desc: str, elapsed_ms: float):
    print(f"\n{BOLD}{CYAN}┌─────────────────────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{BOLD}{CYAN}│ STAGE {stage_num}: {stage_name:<38} [⏱️ {elapsed_ms:>6.2f} ms] │{RESET}")
    print(f"{BOLD}{CYAN}│ {agent_desc:<75} │{RESET}")
    print(f"{BOLD}{CYAN}└─────────────────────────────────────────────────────────────────────────────┘{RESET}")


def run_stage_by_stage_trace(raw_input: dict):
    print(f"\n{BOLD}{MAGENTA}==============================================================================={RESET}")
    print(f"{BOLD}{MAGENTA}         OMNISPEC AI: 9-AGENT STAGE-BY-STAGE TRANSFORMATION TRACER             {RESET}")
    print(f"{BOLD}{MAGENTA}==============================================================================={RESET}")

    print(f"\n{BOLD}{YELLOW}📥 RAW INPUT RECORD (STAGE 0):{RESET}")
    for k, v in raw_input.items():
        print(f"  • {k:<18}: {BOLD}{v}{RESET}")

    state = ProductEnrichmentState(
        row_id="demo_trace_1",
        raw_mfg_part_num=raw_input.get("Mfg_Part_Num", ""),
        raw_part_desc=raw_input.get("Part_Desc", ""),
        raw_e1_brand=raw_input.get("E1_Brand", ""),
        raw_unilog_brand=raw_input.get("Unilog_Brand", ""),
        raw_dib_brand=raw_input.get("DIB_Brand", ""),
        raw_part_manuf=raw_input.get("Part_Manuf", ""),
        raw_sku=raw_input.get("SKU", "10001")
    )

    # 1. Ingestion
    t0 = time.perf_counter()
    state = state.model_copy(update=IngestionAgent.execute(state))
    ms1 = (time.perf_counter() - t0) * 1000
    print_stage_banner(1, "Ingestion & De-Noising", "Agent 1: Strips placeholder tokens, normalizes casing & parses vendor codes", ms1)
    print(f"  {GREEN}✓ Cleaned Description:{RESET} {state.cleaned_part_desc}")
    print(f"  {GREEN}✓ Supplier Name:{RESET}       {state.clean_supplier_name} (Code: {state.supplier_vendor_code or 'None'})")
    print(f"  {GREEN}✓ Extracted Dim Tokens:{RESET}{state.token_bag.get('dimensions', [])}")

    # 2. Entity Resolution
    t0 = time.perf_counter()
    state = state.model_copy(update=EntityResolutionAgent.execute(state))
    ms2 = (time.perf_counter() - t0) * 1000
    print_stage_banner(2, "Brand & Entity Resolution", "Agent 2: Resolves UniCat 27K legal casing & injects registered marks (®, ™)", ms2)
    print(f"  {GREEN}✓ MANUFACTURER_NAME:{RESET}   {BOLD}{state.manufacturer_name}{RESET}")
    print(f"  {GREEN}✓ BRAND_NAME:{RESET}          {BOLD}{state.brand_name}{RESET}")
    print(f"  {GREEN}✓ TRADE_NAME:{RESET}          {state.trade_name or '—'}")

    # 3. Taxonomy
    t0 = time.perf_counter()
    state = state.model_copy(update=TaxonomyClassifierAgent.execute(state))
    ms3 = (time.perf_counter() - t0) * 1000
    print_stage_banner(3, "Taxonomy & UNSPSC Classification", "Agent 3: Maps tokens into 4-tier Classpath and 8-digit UNSPSC code", ms3)
    print(f"  {GREEN}✓ Classpath (4-Tier):{RESET} {BOLD}{state.classpath}{RESET}")
    print(f"  {GREEN}✓ UNSPSC Code:{RESET}        {state.unspsc}")

    # 4. Spec Extractor
    t0 = time.perf_counter()
    state = state.model_copy(update=SpecUOMExtractorAgent.execute(state))
    ms4 = (time.perf_counter() - t0) * 1000
    print_stage_banner(4, "Spec, Dimension & UOM Extractor", "Agent 4: Extracts L x W x H, converts 63 decimal fractions & formats UOMs", ms4)
    print(f"  {GREEN}✓ Dimensions (L x W x H):{RESET} {state.dimensions.get('LENGTH', '—')} x {state.dimensions.get('WIDTH', '—')} x {state.dimensions.get('HEIGHT', '—')} {state.dimensions.get('LENGTH_UOM', 'in')}")
    print(f"  {GREEN}✓ Electrical / Acoustic:{RESET} {state.electrical_specs or '—'} | {state.acoustic_specs or '—'}")

    # 5. OEM Sourcing
    t0 = time.perf_counter()
    state = state.model_copy(update=OEMSourcingRAGAgent.execute(state))
    ms5 = (time.perf_counter() - t0) * 1000
    print_stage_banner(5, "Autonomous OEM Sourcing RAG", "Agent 5: Discovers official OEM URLs & regulatory approvals (banning marketplaces)", ms5)
    print(f"  {GREEN}✓ MFR URL:{RESET}             {state.mfr_url}")
    print(f"  {GREEN}✓ Standard Approvals:{RESET}  {state.standard_approvals or '—'}")

    # 6. LOV Mapper
    t0 = time.perf_counter()
    state = state.model_copy(update=ConstrainedLOVMapperAgent.execute(state))
    ms6 = (time.perf_counter() - t0) * 1000
    print_stage_banner(6, "Constrained LOV Attribute Mapper", "Agent 6: Binds active schema into 50 triples [LABEL, VALUE, UOM] (150 cols)", ms6)
    for idx in range(1, 10):
        lbl = state.attributes.get(f"ATTRIBUTE_LABEL {idx}")
        val = state.attributes.get(f"ATTRIBUTE_VALUE {idx}")
        uom = state.attributes.get(f"ATTRIBUTE_UOM {idx}")
        if lbl:
            uom_str = f" [{uom}]" if uom else ""
            print(f"     [{idx:02d}] {lbl:<26}: {BOLD}{val}{uom_str}{RESET}")

    # 7. Copy Builder
    t0 = time.perf_counter()
    state = state.model_copy(update=MultiChannelCopyAgent.execute(state))
    ms7 = (time.perf_counter() - t0) * 1000
    print_stage_banner(7, "Multi-Channel Copy Builder", "Agent 7: Generates 6 description tiers adhering to strict character caps & casing", ms7)
    print(f"  {GREEN}✓ INVOICE_DESC (≤40 CAPS):{RESET} {YELLOW}{state.invoice_desc}{RESET} ({len(state.invoice_desc)} chars)")
    print(f"  {GREEN}✓ MOBILE_DESC (60–80):{RESET}     {YELLOW}{state.mobile_desc}{RESET} ({len(state.mobile_desc)} chars)")
    print(f"  {GREEN}✓ SHORT_DESC (Title):{RESET}      {BOLD}{state.short_desc}{RESET}")

    # 8. Digital Assets
    t0 = time.perf_counter()
    state = state.model_copy(update=DigitalAssetAgent.execute(state))
    ms8 = (time.perf_counter() - t0) * 1000
    print_stage_banner(8, "Digital Asset Synthesizer", "Agent 8: Synthesizes canonical <Brand>_<MPN> images and PDF spec sheets", ms8)
    print(f"  {GREEN}✓ Product Image Asset:{RESET}  {state.digital_assets.get('Product Image')}")
    print(f"  {GREEN}✓ Specification Sheet:{RESET}  {state.digital_assets.get('Specification Sheet')}")

    # 9. Quality Audit
    t0 = time.perf_counter()
    state = state.model_copy(update=QualityAuditAgent.execute(state))
    ms9 = (time.perf_counter() - t0) * 1000
    print_stage_banner(9, "Quality Audit & HITL Gate", "Agent 9: Executes 12-point integrity suite and computes weighted confidence", ms9)
    print(f"  {GREEN}✓ Overall Record Confidence:{RESET} {BOLD}{state.overall_confidence * 100:.1f}%{RESET}")
    print(f"  {GREEN}✓ Integrity Violations:{RESET}      {state.integrity_violations or 'None (100% Compliant)'}")

    total_time = ms1 + ms2 + ms3 + ms4 + ms5 + ms6 + ms7 + ms8 + ms9
    print(f"\n{BOLD}{GREEN}==============================================================================={RESET}")
    print(f"{BOLD}{GREEN}  TRANSFORMATION COMPLETE: 252-COLUMN MASTER RECORD GENERATED IN {total_time:.2f} ms!  {RESET}")
    print(f"{BOLD}{GREEN}==============================================================================={RESET}\n")


if __name__ == "__main__":
    sample = {
        "Mfg_Part_Num": "PDSH4816AF",
        "Part_Desc": "PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA",
        "Part_Manuf": "Appliance Dealers Cooperative (APPDE)",
        "E1_Brand": "-- Unbranded --",
        "Unilog_Brand": "-- No Unilog Brand --",
        "DIB_Brand": "-- No DIB Brand --",
        "SKU": "10001"
    }
    run_stage_by_stage_trace(sample)
