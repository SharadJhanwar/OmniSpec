import time
import re
from typing import Dict, Any, List
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..services.evidence_discovery_service import EvidenceDiscoveryService
from ..core.logging import logger


class OEMSourcingRAGAgent:
    """
    Agent 5: Autonomous OEM Sourcing & CRAG (Corrective RAG) Agent
    Implements pure dynamic CRAG evidence discovery:
    1. Triggers targeted web search via DuckDuckGo for "{Brand} {MPN} datasheet technical specifications pdf".
    2. Evaluates source quality (OEM / Technical PDF > Authorized Distributor; Marketplaces Discarded).
    3. Reranks evidence snippets by semantic cosine relevance and technical spec density.
    4. Extracts authoritative URLs and grounds approvals strictly in verified evidence.
    Zero hardcoded domain or URL dictionaries.
    """

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        mpn = (state.clean_mfg_part_num or "").strip()
        brand = (state.brand_name or "").strip()
        desc = state.cleaned_part_desc or ""

        mfr_url = ""
        ref_urls: List[str] = []
        approvals = ""
        crag_grade = "CORRECT"
        discovered_snippets: List[str] = []

        # 1. Targeted Evidence Discovery via Search Crawler
        if mpn:
            raw_evidence = EvidenceDiscoveryService.discover_web_evidence(
                mpn=mpn,
                brand=brand if brand != "-- Unbranded --" else "",
                desc=desc,
                max_results=4
            )

            if raw_evidence:
                reranked_evidence = EvidenceDiscoveryService.rank_best_evidence(
                    query=f"{brand} {mpn} {desc}",
                    evidence_items=raw_evidence,
                    top_k=2
                )
                if reranked_evidence:
                    top_ev = reranked_evidence[0]
                    mfr_url = top_ev.get("url", "")
                    for ev in reranked_evidence:
                        ref_urls.append(ev.get("url", ""))
                        discovered_snippets.append(ev.get("snippet", ""))
                    crag_grade = "CORRECT" if top_ev.get("source_quality", 0.0) >= 0.85 else "AMBIGUOUS"
            if not mfr_url and brand and brand not in ["-- Unbranded --", "Unassigned", ""]:
                clean_b_str = re.sub(r"[^a-zA-Z0-9]", "", brand).lower()
                if clean_b_str:
                    mfr_url = f"https://www.{clean_b_str}.com"
                    ref_urls.append(mfr_url)

        # 2. Extract Grounded Approvals & Missing Technical Specs from Web Evidence
        combined_snippets = " ".join(discovered_snippets)
        evidence_text = f"{combined_snippets} {desc}".lower()

        # Approvals
        found_approvals = []
        if "energy star" in evidence_text:
            found_approvals.append("ENERGY STAR Certified")
        if "ul listed" in evidence_text or " culus " in evidence_text:
            found_approvals.append("UL Listed")
        if "nsf" in evidence_text:
            found_approvals.append("NSF Certified")
        if "osha" in evidence_text:
            found_approvals.append("OSHA Compliant")
        if "ansi" in evidence_text:
            found_approvals.append("ANSI Compliant")
        if "csa" in evidence_text:
            found_approvals.append("CSA Certified")
        if "rohs" in evidence_text:
            found_approvals.append("RoHS Compliant")
        if "iso 9001" in evidence_text or "iso certified" in evidence_text:
            found_approvals.append("ISO 9001 Certified")

        approvals = "|".join(found_approvals) if found_approvals else state.standard_approvals

        # Mine new specs from search snippets to enrich state
        new_elec = dict(state.electrical_specs)
        new_dims = dict(state.dimensions)
        new_acoust = dict(state.acoustic_specs)
        new_pack = dict(state.packaging_specs)
        new_warranty = state.warranty or ""
        new_upc = state.upc or ""

        if combined_snippets:
            # 1. Electrical & Power
            if "Voltage Rating" not in new_elec:
                volt_m = re.search(r"\b(\d{2,3})\s*(?:V|VAC|Volts)\b", combined_snippets, re.I)
                if volt_m:
                    new_elec["Voltage Rating"] = volt_m.group(1)
                    new_elec["Voltage Rating UOM"] = "V"

            if "Amperage Rating" not in new_elec:
                amp_m = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:A|Amps|Amperes)\b", combined_snippets, re.I)
                if amp_m:
                    new_elec["Amperage Rating"] = amp_m.group(1)
                    new_elec["Amperage Rating UOM"] = "A"

            if "Wattage" not in new_elec:
                watt_m = re.search(r"\b(\d{2,5})\s*(?:W|Watts|Wattage)\b", combined_snippets, re.I)
                if watt_m:
                    new_elec["Wattage"] = watt_m.group(1)
                    new_elec["Wattage UOM"] = "W"

            # 2. Acoustic
            if "Sound Level" not in new_acoust:
                sound_m = re.search(r"\b(\d{2})\s*(?:dBA|dB|Decibels)\b", combined_snippets, re.I)
                if sound_m:
                    new_acoust["Sound Level"] = sound_m.group(1)
                    new_acoust["Sound Level UOM"] = "dBA"

            # 3. Pressure & Speed
            if "Pressure Rating" not in new_elec:
                psi_m = re.search(r"\b(\d{2,5})\s*(?:PSI|psi)\b", combined_snippets, re.I)
                if psi_m:
                    new_elec["Pressure Rating"] = psi_m.group(1)
                    new_elec["Pressure Rating UOM"] = "PSI"

            if "Speed Rating" not in new_elec and "Max Speed" not in new_elec:
                rpm_m = re.search(r"\b(\d{3,5})\s*(?:RPM|rpm)\b", combined_snippets, re.I)
                if rpm_m:
                    new_elec["Speed Rating"] = rpm_m.group(1)
                    new_elec["Speed Rating UOM"] = "rpm"

            # 4. Grit
            if "Grit" not in new_elec:
                grit_m = re.search(r"\b(?:P\s*(\d{2,4})|(\d{2,4})\s*Grit)\b", combined_snippets, re.I)
                if grit_m:
                    g_val = grit_m.group(1) or grit_m.group(2)
                    new_elec["Grit"] = f"P{g_val}" if "P" in combined_snippets else g_val

            # 5. UPC / GTIN
            if not new_upc:
                upc_m = re.search(r"\b(?:UPC|GTIN)[:\s]+(\d{12,14})\b", combined_snippets, re.I)
                if upc_m:
                    new_upc = upc_m.group(1)

            # 6. Warranty
            if not new_warranty:
                warr_m = re.search(r"\b(\d+[- ]Year (?:Limited )?Warranty|Lifetime (?:Limited )?Warranty)\b", combined_snippets, re.I)
                if warr_m:
                    new_warranty = warr_m.group(1)

            # 7. Material & Finish
            if "Material" not in new_elec:
                if "stainless steel" in combined_snippets.lower():
                    new_elec["Material"] = "Stainless Steel"
                    new_elec["Finish"] = "Stainless Steel"
                elif "cast iron" in combined_snippets.lower():
                    new_elec["Material"] = "Cast Iron"
                elif "aluminum" in combined_snippets.lower():
                    new_elec["Material"] = "Aluminum"
                elif "carbide" in combined_snippets.lower():
                    new_elec["Material"] = "Solid Carbide"

            if "Color" not in new_elec:
                if "white" in combined_snippets.lower():
                    new_elec["Color"] = "White"
                elif "black" in combined_snippets.lower():
                    new_elec["Color"] = "Black"

        # 3. Discard banned marketplace URLs
        filtered_ref_urls = [
            u for u in ref_urls
            if EvidenceDiscoveryService.evaluate_source_quality(u) > 0.0
        ]
        if EvidenceDiscoveryService.evaluate_source_quality(mfr_url) == 0.0:
            mfr_url = ""

        trace = AgentTrace(
            agent_name="Agent 5: OEM Sourcing & CRAG",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"CRAG Grade: {crag_grade}",
                f"Discovered OEM URL: {mfr_url or 'None'}",
                f"Grounded Approvals: {approvals or 'None'}",
                f"Authoritative Snippets Reranked: {len(discovered_snippets)}",
                f"Web-Discovered Specs Mined: {len(new_elec) - len(state.electrical_specs)}"
            ],
            extracted_data={
                "mfr_url": mfr_url,
                "ref_urls": filtered_ref_urls,
                "standard_approvals": approvals,
                "crag_grade": crag_grade,
                "discovered_evidence": discovered_snippets,
                "mined_specs": {k: v for k, v in new_elec.items() if k not in state.electrical_specs}
            }
        )

        return {
            "mfr_url": mfr_url,
            "ref_urls": filtered_ref_urls,
            "standard_approvals": approvals,
            "electrical_specs": new_elec,
            "dimensions": new_dims,
            "acoustic_specs": new_acoust,
            "packaging_specs": new_pack,
            "warranty": new_warranty,
            "upc": new_upc,
            "traces": state.traces + [trace]
        }
