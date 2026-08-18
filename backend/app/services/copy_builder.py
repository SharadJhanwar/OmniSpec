from typing import Dict, List, Optional
from ..schemas.state_schema import ProductEnrichmentState


class MultiChannelCopyBuilder:
    """
    Constructs multi-channel descriptions adhering strictly to character limits,
    casing rules, and formulas defined in Unilog Internal Content Guidelines.
    """

    @classmethod
    def build_invoice_desc(cls, product_name: str, mounting: str, specs: str, volts: str, amps: str, dimension: str) -> str:
        """
        Formula: <ITEM_TYPE> <MOUNTING> <KEY_SPEC> <VOLTAGE> <CURRENT> <DIMENSION>
        Constraint: <= 40 characters, strictly UPPERCASE
        Example: 'DISHWASHER LEG 5 SST 120V 15A 50-1/4IN'
        """
        tokens = []
        if product_name:
            tokens.append(product_name.upper())
        if mounting:
            # Condense mounting: 'Built-in' -> 'BLTLN', 'Leg Mounting' -> 'LEG'
            m_clean = mounting.upper().replace("MOUNTING", "").strip()
            if "BUILT-IN" in m_clean or "BUILTIN" in m_clean:
                tokens.append("BLTLN")
            elif "LEG" in m_clean:
                tokens.append("LEG")
            else:
                tokens.append(m_clean[:5])
        if specs:
            tokens.append(specs.upper())
        if volts:
            tokens.append(f"{volts.upper().replace(' ', '')}V" if not volts.upper().endswith("V") else volts.upper())
        if amps:
            tokens.append(f"{amps.upper().replace(' ', '')}A" if not amps.upper().endswith("A") else amps.upper())
        if dimension:
            tokens.append(dimension.upper().replace(" ", ""))

        raw_invoice = " ".join(tokens).strip()

        # Enforce hard <= 40 character limit
        if len(raw_invoice) > 40:
            return raw_invoice[:40]
        return raw_invoice

    @classmethod
    def build_mobile_desc(cls, mfr_name: str, brand_name: str, product_name: str, series: str, mpn: str) -> str:
        """
        Formula: <MANUFACTURER_NAME> <BRAND_NAME>, <ITEM_TYPE>, <SERIES>, <MPN>
        Constraint: 60 to 80 characters
        Example: 'Rheem Manufacturing FRIGIDAIRE, Dishwasher, Professional Series, PDSH4816AF'
        """
        clean_brand = brand_name.replace("®", "").replace("™", "").strip()
        parts = []

        # Start with MFR and Brand
        if mfr_name and mfr_name != clean_brand:
            parts.append(f"{mfr_name} {clean_brand}")
        else:
            parts.append(clean_brand)

        if product_name:
            parts.append(product_name)
        if series:
            parts.append(series)
        if mpn:
            parts.append(mpn)

        candidate = ", ".join(parts)

        # Pad or trim to fit 60-80 chars window if possible
        if len(candidate) < 60:
            # Add descriptive context if too short
            if series and "Series" not in series:
                parts.insert(2, f"{series} Series")
                candidate = ", ".join(parts)

        return candidate

    @classmethod
    def build_short_desc(cls, brand_name: str, series: str, mpn: str, product_name: str, with_feat: str, key_specs: str) -> str:
        """
        Formula: <BRAND_NAME> <SERIES> <MPN> <PRODUCT_NAME> <WITH>, <KEY_SPECS>
        Example: 'FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel'
        """
        parts = []
        head = []
        if brand_name:
            head.append(brand_name)
        if series:
            head.append(series)
        if mpn:
            head.append(mpn)
        if product_name:
            head.append(product_name)
        if with_feat:
            head.append(with_feat)

        title_head = " ".join(head).strip()
        if key_specs:
            return f"{title_head}, {key_specs}"
        return title_head
