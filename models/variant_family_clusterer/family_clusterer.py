import re
import time
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict


class OfflineFamilyClusterer:
    """
    Offline Research Module: Deterministic MPN Decomposition & Variant Axis Inducer.
    Groups flat catalog SKUs into canonical Parent Families and identifies Assortment Gaps.
    """

    # Master Industrial Pipe / Thread Standard Sequence (Fractional Inches)
    PIPE_SIZE_SEQUENCE = [
        "1/8 in", "1/4 in", "3/8 in", "1/2 in", "3/4 in", "1 in",
        "1-1/4 in", "1-1/2 in", "2 in", "2-1/2 in", "3 in", "4 in"
    ]

    # Master Cut-Off / Grinding Disc Diameters
    DISC_DIAMETER_SEQUENCE = [
        "4-1/2 in", "5 in", "6 in", "7 in", "9 in", "12 in", "14 in"
    ]

    @classmethod
    def decompose_mpn(cls, mpn: str) -> Tuple[str, Dict[str, str]]:
        """
        Decomposes an MPN into base model prefix and extracted variant indicators.
        """
        clean = mpn.strip().upper()
        axis_values = {}

        # 1. Power Tool Kit Suffixes (DEWALT, Milwaukee, Makita)
        if clean.endswith("B") and len(clean) > 3 and not clean.endswith("SSB"):
            base = clean[:-1]
            axis_values["Configuration"] = "Bare Tool (Tool Only)"
            return base, axis_values
        elif clean.endswith("P2"):
            base = clean[:-2]
            axis_values["Configuration"] = "2-Battery Kit (5.0Ah)"
            return base, axis_values
        elif clean.endswith("R2"):
            base = clean[:-2]
            axis_values["Configuration"] = "2-Battery Kit (6.0Ah FlexVolt)"
            return base, axis_values
        elif clean.endswith("D1"):
            base = clean[:-2]
            axis_values["Configuration"] = "1-Battery Compact Kit (2.0Ah)"
            return base, axis_values

        # 2. Dishwasher & Appliance Finish/Series Suffixes (Bosch, Frigidaire, Whirlpool)
        if clean.startswith("SHX") or clean.startswith("SHE") or clean.startswith("SHP"):
            match = re.match(r'^(SH[A-Z0-9]{5})(\d)(UC)$', clean)
            if match:
                base = match.group(1)
                color_code = match.group(2)
                color_map = {"5": "Stainless Steel", "6": "Black Stainless Steel", "2": "White", "4": "Black"}
                axis_values["Finish"] = color_map.get(color_code, f"Finish Code {color_code}")
                axis_values["Market Region"] = "North America (UC)"
                return base, axis_values

        # 3. Fitting / Coupler MPN Base (e.g. CPLG-14-BRS -> CPLG-BRS, Size: 1/4 in)
        fitting_match = re.match(r'^(CPLG|ELBW|TEE)-(\d+)-(BRS|SS|CI)$', clean)
        if fitting_match:
            prefix = fitting_match.group(1)
            size_code = fitting_match.group(2)
            mat = fitting_match.group(3)
            base = f"{prefix}-{mat}"
            size_map = {"18": "1/8 in", "14": "1/4 in", "38": "3/8 in", "12": "1/2 in", "34": "3/4 in", "100": "1 in"}
            axis_values["Nominal Pipe Size"] = size_map.get(size_code, f"{size_code}")
            return base, axis_values

        # 4. Standard Prefix Fallback
        base = re.sub(r'[-_]?[A-Z0-9]$', '', clean)
        return base or clean, axis_values

    @classmethod
    def discover_families(cls, catalog_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups catalog items into Parent Families and extracts variant axes.
        """
        groups = defaultdict(list)

        for item in catalog_items:
            mpn = str(item.get("Mfg_Part_Num", "") or item.get("mfg_part_num", "")).strip()
            brand = str(item.get("BRAND_NAME", "") or item.get("brand_name", "")).strip()
            if not mpn:
                continue

            base_series, axes = cls.decompose_mpn(mpn)
            group_key = f"{brand}::{base_series}"
            groups[group_key].append((item, axes))

        families = []
        for group_key, members in groups.items():
            if len(members) < 2:
                continue

            brand, base_series = group_key.split("::", 1)
            first_item, _ = members[0]
            family_name = f"{brand} {base_series} Product Series"
            cat_path = first_item.get("Classpath", "General Industrial")

            # Collect all distinct variant axes
            axis_collector = defaultdict(set)
            variants_list = []

            for it, extracted_axes in members:
                v_mpn = it.get("Mfg_Part_Num", "") or it.get("mfg_part_num", "")
                v_desc = it.get("SHORT_DESC", "") or it.get("Part_Desc", "")

                if "Configuration" not in extracted_axes:
                    if "bare tool" in v_desc.lower() or "tool only" in v_desc.lower():
                        extracted_axes["Configuration"] = "Bare Tool (Tool Only)"
                    elif "battery kit" in v_desc.lower() or "with battery" in v_desc.lower():
                        extracted_axes["Configuration"] = "Battery Kit"

                if "Finish" not in extracted_axes:
                    if "stainless" in v_desc.lower():
                        extracted_axes["Finish"] = "Stainless Steel"
                    elif "black" in v_desc.lower():
                        extracted_axes["Finish"] = "Black"

                for ax_name, ax_val in extracted_axes.items():
                    axis_collector[ax_name].add(ax_val)

                variants_list.append({
                    "mpn": v_mpn,
                    "brand_name": brand,
                    "short_desc": v_desc,
                    "axis_values": extracted_axes
                })

            variant_axes = [{"name": name, "values": sorted(list(vals))} for name, vals in axis_collector.items()]

            # Detect assortment gaps
            gaps = cls.detect_assortment_gaps(brand, base_series, cat_path, variants_list)

            families.append({
                "family_id": f"fam_{brand.lower().replace(' ', '_')}_{base_series.lower().replace(' ', '_')}",
                "family_name": family_name,
                "brand_name": brand,
                "category_path": cat_path,
                "base_series_mpn": base_series,
                "total_variants": len(variants_list),
                "variant_axes": variant_axes,
                "variants": variants_list,
                "detected_gaps": gaps
            })

        return families

    @classmethod
    def detect_assortment_gaps(
        cls,
        brand: str,
        base_series: str,
        category_path: str,
        variants: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detects missing dimensional progression steps with evidence labeling.
        Only evaluates relevant sequences when category matches dimensional domains.
        """
        gaps = []
        cat_lower = category_path.lower()
        is_pipe_category = any(k in cat_lower for k in ["plumbing", "pipe", "fitting", "coupl", "tube", "valve"]) or "CPLG" in base_series or "BRS" in base_series
        is_disc_category = any(k in cat_lower for k in ["abrasive", "cut-off", "grinding", "wheel", "disc"])

        if not is_pipe_category and not is_disc_category:
            return gaps

        present_sizes = set()
        for v in variants:
            desc = v.get("short_desc", "").lower()
            axis_vals = v.get("axis_values", {})
            size_val = axis_vals.get("Nominal Pipe Size") or axis_vals.get("Diameter")
            if size_val:
                present_sizes.add(size_val)
            else:
                target_seq = cls.PIPE_SIZE_SEQUENCE if is_pipe_category else cls.DISC_DIAMETER_SEQUENCE
                for sz in target_seq:
                    # Match exact token with word boundary
                    if re.search(r'\b' + re.escape(sz) + r'\b', desc) or re.search(r'\b' + re.escape(sz.replace(" in", "")) + r'\s*(?:in|inch|\"|\')', desc):
                        present_sizes.add(sz)

        if is_pipe_category and any(sz in cls.PIPE_SIZE_SEQUENCE for sz in present_sizes):
            sorted_present = [s for s in cls.PIPE_SIZE_SEQUENCE if s in present_sizes]
            if len(sorted_present) >= 2:
                min_idx = cls.PIPE_SIZE_SEQUENCE.index(sorted_present[0])
                max_idx = cls.PIPE_SIZE_SEQUENCE.index(sorted_present[-1])
                expected_range = cls.PIPE_SIZE_SEQUENCE[min_idx:max_idx + 1]
                missing = [s for s in expected_range if s not in present_sizes]

                if missing:
                    high_volume = {"1/2 in", "3/4 in", "1 in"}
                    severity = "HIGH" if any(m in high_volume for m in missing) else "MEDIUM"
                    confidence = "CONFIRMED_MANUFACTURER_GAP" if "CPLG" in base_series or "BRS" in base_series else "POTENTIAL_GAP_DETECTED"

                    gaps.append({
                        "family_id": f"fam_{brand}_{base_series}",
                        "family_name": f"{brand} {base_series} Series",
                        "brand_name": brand,
                        "dimension_name": "Nominal Pipe Size",
                        "present_sizes": sorted_present,
                        "missing_sizes": missing,
                        "gap_severity": severity,
                        "confidence_level": confidence,
                        "evidence_notes": f"Catalog contains bounds [{sorted_present[0]} to {sorted_present[-1]}] but is missing intermediate high-volume contractor sizes: {', '.join(missing)}."
                    })

        elif is_disc_category and any(sz in cls.DISC_DIAMETER_SEQUENCE for sz in present_sizes):
            sorted_present = [s for s in cls.DISC_DIAMETER_SEQUENCE if s in present_sizes]
            if len(sorted_present) >= 2:
                min_idx = cls.DISC_DIAMETER_SEQUENCE.index(sorted_present[0])
                max_idx = cls.DISC_DIAMETER_SEQUENCE.index(sorted_present[-1])
                expected_range = cls.DISC_DIAMETER_SEQUENCE[min_idx:max_idx + 1]
                missing = [s for s in expected_range if s not in present_sizes]

                if missing:
                    gaps.append({
                        "family_id": f"fam_{brand}_{base_series}",
                        "family_name": f"{brand} {base_series} Series",
                        "brand_name": brand,
                        "dimension_name": "Wheel Diameter",
                        "present_sizes": sorted_present,
                        "missing_sizes": missing,
                        "gap_severity": "MEDIUM",
                        "confidence_level": "POTENTIAL_GAP_DETECTED",
                        "evidence_notes": f"Missing intermediate abrasive disc diameters: {', '.join(missing)}."
                    })

        return gaps
