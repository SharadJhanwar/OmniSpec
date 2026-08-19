import sys
import io
import time
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

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
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_stage_banner(stage_num: int, stage_name: str, agent_desc: str, elapsed_ms: float):
    print(f"\n{BOLD}{CYAN}-------------------------------------------------------------------------------{RESET}")
    print(f"{BOLD}{CYAN}[STAGE {stage_num}] {stage_name:<40} (Execution: {elapsed_ms:>6.2f} ms){RESET}")
    print(f"{CYAN}{agent_desc}{RESET}")
    print(f"{BOLD}{CYAN}-------------------------------------------------------------------------------{RESET}")


def run_stage_by_stage_trace(raw_input: dict):
    print(f"\n{BOLD}{MAGENTA}==============================================================================={RESET}")
    print(f"{BOLD}{MAGENTA}         OMNISPEC AI: 9-AGENT STAGE-BY-STAGE TRANSFORMATION TRACER             {RESET}")
    print(f"{BOLD}{MAGENTA}==============================================================================={RESET}")

    print(f"\n{BOLD}{YELLOW}>> RAW INPUT RECORD (STAGE 0):{RESET}")
    for k, v in raw_input.items():
        print(f"  * {k:<18}: {BOLD}{v}{RESET}")

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

    # -------------------------------------------------------------
    # STAGE 1: INGESTION & DE-NOISING
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out1 = IngestionAgent.execute(state)
    state = state.model_copy(update=out1)
    ms1 = (time.perf_counter() - t0) * 1000
    print_stage_banner(1, "Ingestion & De-Noising", "Agent 1: Strips placeholder tokens, normalizes casing & parses vendor codes", ms1)
    print(f"  {GREEN}[+] Cleaned Description:{RESET} {state.cleaned_part_desc}")
    print(f"  {GREEN}[+] Supplier Name:{RESET}       {state.clean_supplier_name} (Code: {state.supplier_vendor_code or 'None'})")
    print(f"  {GREEN}[+] Extracted Dim Tokens:{RESET}{state.token_bag.get('dimensions', [])}")
    print(f"  {GREEN}[+] Pack Qty Detected:{RESET}   {state.token_bag.get('pack_qty') or '1 (Each)'}")

    # -------------------------------------------------------------
    # STAGE 2: BRAND & ENTITY RESOLUTION
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out2 = EntityResolutionAgent.execute(state)
    state = state.model_copy(update=out2)
    ms2 = (time.perf_counter() - t0) * 1000
    print_stage_banner(2, "Brand & Entity Resolution", "Agent 2: Resolves UniCat 27K legal casing & injects registered marks (®, ™)", ms2)
    print(f"  {GREEN}[+] MANUFACTURER_NAME:{RESET}   {BOLD}{state.manufacturer_name}{RESET}")
    print(f"  {GREEN}[+] BRAND_NAME:{RESET}          {BOLD}{state.brand_name}{RESET}")
    print(f"  {GREEN}[+] TRADE_NAME:{RESET}          {state.trade_name or '—'}")
    print(f"  {GREEN}[+] MPN / ALT_PART_NUM:{RESET}  {state.mfr_part_number} / {state.alt_part_number or '—'}")
    print(f"  {GREEN}[+] Brand Confidence:{RESET}    {state.brand_confidence * 100:.1f}%")

    # -------------------------------------------------------------
    # STAGE 3: TAXONOMY CLASSIFICATION & UNSPSC
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out3 = TaxonomyClassifierAgent.execute(state)
    state = state.model_copy(update=out3)
    ms3 = (time.perf_counter() - t0) * 1000
    print_stage_banner(3, "Taxonomy & UNSPSC Classification", "Agent 3: Maps tokens into 4-tier Classpath and 8-digit UNSPSC code", ms3)
    print(f"  {GREEN}[+] Classpath (4-Tier):{RESET} {BOLD}{state.classpath}{RESET}")
    print(f"  {GREEN}[+] UNSPSC Code:{RESET}        {state.unspsc}")
    print(f"  {GREEN}[+] Department / Class:{RESET} {state.dept} > {state.class_name} > {state.fine}")
    print(f"  {GREEN}[+] Canonical Product:{RESET}  {state.product_name}")

    # -------------------------------------------------------------
    # STAGE 4: PRECISION SPEC, DIMENSION & UOM EXTRACTOR
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out4 = SpecUOMExtractorAgent.execute(state)
    state = state.model_copy(update=out4)
    ms4 = (time.perf_counter() - t0) * 1000
    print_stage_banner(4, "Spec, Dimension & UOM Extractor", "Agent 4: Extracts L x W x H, converts 63 decimal fractions & formats UOMs", ms4)
    print(f"  {GREEN}[+] Dimensions (L x W x H):{RESET} {state.dimensions.get('LENGTH', '—')} x {state.dimensions.get('WIDTH', '—')} x {state.dimensions.get('HEIGHT', '—')} {state.dimensions.get('LENGTH_UOM', 'in')}")
    print(f"  {GREEN}[+] Electrical Ratings:{RESET}     {state.electrical_specs or '—'}")
    print(f"  {GREEN}[+] Acoustic Rating:{RESET}        {state.acoustic_specs or '—'}")
    print(f"  {GREEN}[+] Selling Qty & UOM:{RESET}      {state.packaging_specs.get('Selling Qty', '1')} {state.packaging_specs.get('Selling UOM', 'Each')}")

    # -------------------------------------------------------------
    # STAGE 5: OEM SOURCING & SPEC SHEET RAG
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out5 = OEMSourcingRAGAgent.execute(state)
    state = state.model_copy(update=out5)
    ms5 = (time.perf_counter() - t0) * 1000
    print_stage_banner(5, "Autonomous OEM Sourcing RAG", "Agent 5: Discovers official OEM URLs & regulatory approvals (banning marketplaces)", ms5)
    print(f"  {GREEN}[+] MFR URL:{RESET}             {state.mfr_url}")
    print(f"  {GREEN}[+] Ref / Spec URL:{RESET}      {state.ref_urls[0] if state.ref_urls else '—'}")
    print(f"  {GREEN}[+] Standard Approvals:{RESET}  {state.standard_approvals or '—'}")

    # -------------------------------------------------------------
    # STAGE 6: CONSTRAINED LOV ATTRIBUTE MAPPER (150-COL EAV)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out6 = ConstrainedLOVMapperAgent.execute(state)
    state = state.model_copy(update=out6)
    ms6 = (time.perf_counter() - t0) * 1000
    print_stage_banner(6, "Constrained LOV Attribute Mapper", "Agent 6: Binds active schema into 50 triples [LABEL, VALUE, UOM] (150 cols)", ms6)
    print(f"  {GREEN}[+] Allocated Attribute Triples (Showing non-empty slots):{RESET}")
    for idx in range(1, 51):
        lbl = state.attributes.get(f"ATTRIBUTE_LABEL {idx}")
        val = state.attributes.get(f"ATTRIBUTE_VALUE {idx}")
        uom = state.attributes.get(f"ATTRIBUTE_UOM {idx}")
        if lbl:
            uom_str = f" [{uom}]" if uom else ""
            print(f"     [{idx:02d}] {lbl:<26}: {BOLD}{val}{uom_str}{RESET}")
    print(f"  {GREEN}[+] Special Fields:{RESET}       With: '{state.with_features}' | Warranty: '{state.warranty}'")

    # -------------------------------------------------------------
    # STAGE 7: MULTI-CHANNEL FORMULAIC COPY BUILDER
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out7 = MultiChannelCopyAgent.execute(state)
    state = state.model_copy(update=out7)
    ms7 = (time.perf_counter() - t0) * 1000
    print_stage_banner(7, "Multi-Channel Copy Builder", "Agent 7: Generates 6 description tiers adhering to strict character caps & casing", ms7)
    print(f"  {GREEN}[+] INVOICE_DESC (<=40 CAPS):{RESET} {YELLOW}{state.invoice_desc}{RESET} ({len(state.invoice_desc)} chars)")
    print(f"  {GREEN}[+] MOBILE_DESC (60-80):{RESET}     {YELLOW}{state.mobile_desc}{RESET} ({len(state.mobile_desc)} chars)")
    print(f"  {GREEN}[+] SHORT_DESC (Title):{RESET}      {BOLD}{state.short_desc}{RESET}")
    print(f"  {GREEN}[+] LONG_DESC1:{RESET}              {state.long_desc1[:140]}...")
    print(f"  {GREEN}[+] Features (1..{len(state.item_features)}):{RESET}        {state.item_features[:3]}")

    # -------------------------------------------------------------
    # STAGE 8: DIGITAL ASSET SYNTHESIZER
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out8 = DigitalAssetAgent.execute(state)
    state = state.model_copy(update=out8)
    ms8 = (time.perf_counter() - t0) * 1000
    print_stage_banner(8, "Digital Asset Synthesizer", "Agent 8: Synthesizes canonical <Brand>_<MPN> images and PDF spec sheets", ms8)
    print(f"  {GREEN}[+] Product Image Asset:{RESET}  {state.digital_assets.get('Product Image')}")
    print(f"  {GREEN}[+] Specification Sheet:{RESET}  {state.digital_assets.get('Specification Sheet')}")
    print(f"  {GREEN}[+] Country Of Origin:{RESET}    {state.digital_assets.get('Country Of Origin')}")
    print(f"  {GREEN}[+] Actual Image / Active:{RESET}{state.digital_assets.get('Actual Image (Yes/No)')} / Discontinued: {state.digital_assets.get('Discontinued')}")

    # -------------------------------------------------------------
    # STAGE 9: QUALITY AUDIT & HITL LINEAGE
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    out9 = QualityAuditAgent.execute(state)
    state = state.model_copy(update=out9)
    ms9 = (time.perf_counter() - t0) * 1000
    print_stage_banner(9, "Quality Audit & HITL Gate", "Agent 9: Executes 12-point integrity suite and computes weighted confidence", ms9)
    print(f"  {GREEN}[+] Overall Record Confidence:{RESET} {BOLD}{state.overall_confidence * 100:.1f}%{RESET}")
    print(f"  {GREEN}[+] Integrity Violations:{RESET}      {state.integrity_violations or 'None (100% Compliant)'}")
    print(f"  {GREEN}[+] Needs Human Review (HITL):{RESET}{state.needs_hitl_review}")

    total_time = ms1 + ms2 + ms3 + ms4 + ms5 + ms6 + ms7 + ms8 + ms9
    print(f"\n{BOLD}{GREEN}==============================================================================={RESET}")
    print(f"{BOLD}{GREEN}  TRANSFORMATION COMPLETE: 252-COLUMN MASTER RECORD GENERATED IN {total_time:.2f} ms!  {RESET}")
    print(f"{BOLD}{GREEN}==============================================================================={RESET}\n")


if __name__ == "__main__":
    presets = [
        {
            "name": "1. Large Appliances (Frigidaire Built-In Dishwasher)",
            "input": {
                "Mfg_Part_Num": "PDSH4816AF",
                "Part_Desc": "PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA",
                "Part_Manuf": "Appliance Dealers Cooperative (APPDE)",
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "SKU": "10001"
            }
        },
        {
            "name": "2. Abrasives & Metalworking (Milwaukee Cut-Off Wheel)",
            "input": {
                "Mfg_Part_Num": "49-94-0013",
                "Part_Desc": "49-94-0013 Milw 5\"x.045\"x7/8\" Metal Cut Off Disc",
                "Part_Manuf": "Milwaukee Accessory (4031)",
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "SKU": "10002"
            }
        },
        {
            "name": "3. Building Materials (Trex Composite Decking Board)",
            "input": {
                "Mfg_Part_Num": "1513720",
                "Part_Desc": "1nx6-16' Honey Grove Grooved - Trex Enhance Naturals Decking",
                "Part_Manuf": "Boise Cascade Building Materials (BOICA)",
                "E1_Brand": "TREX",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "SKU": "10003"
            }
        },
        {
            "name": "4. Plumbing & Industrial Pipe Fittings (Brass Coupler)",
            "input": {
                "Mfg_Part_Num": "CPLG-38-BRS",
                "Part_Desc": "3/8 CPLG BRS 150# Female NPT Coupler",
                "Part_Manuf": "Jam Industrial Supply LLC (JAMIN)",
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "SKU": "10004"
            }
        },
        {
            "name": "5. Lighting & Luminaires (Philips LED A19 Bulb)",
            "input": {
                "Mfg_Part_Num": "558213",
                "Part_Desc": "9.5A19/LED/827/FR/P/ND 4/2FB LED A19 60W Equivalent 2700K Medium Base 2PK",
                "Part_Manuf": "Phillips Lighting (5831)",
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "SKU": "10005"
            }
        },
        {
            "name": "6. Power Tools & Saws (DEWALT 20V MAX Miter Saw)",
            "input": {
                "Mfg_Part_Num": "DCS361B",
                "Part_Desc": "DCS361B DEWALT 20V MAX 7-1/4 IN Cordless Sliding Miter Saw Brushless",
                "Part_Manuf": "Black & Decker/dewlt (2585)",
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "SKU": "10006"
            }
        }
    ]

    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        choice = int(sys.argv[1]) - 1
        if 0 <= choice < len(presets):
            print(f"\n{BOLD}Selected Preset:{RESET} {presets[choice]['name']}")
            run_stage_by_stage_trace(presets[choice]["input"])
        else:
            print("Invalid preset index. Running Preset 1 by default.")
            run_stage_by_stage_trace(presets[0]["input"])
    else:
        print(f"\n{BOLD}Running Default Stage-by-Stage Trace on Ground-Truth Worked Example:{RESET}")
        run_stage_by_stage_trace(presets[0]["input"])
