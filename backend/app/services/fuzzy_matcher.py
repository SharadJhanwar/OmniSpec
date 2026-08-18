from typing import Dict, List, Optional, Tuple
from rapidfuzz import process, fuzz


class BrandEntityResolver:
    """
    Resolves supplier and description tokens to canonical UniCat Manufacturers & Brands
    with legal entity suffixes (Inc, LLC, Corp) and registered symbols (®, ™).
    """

    # High-frequency alias lookup for instant sub-millisecond matching
    KNOWN_BRAND_MAP = {
        "MILW": {"mfr": "Milwaukee Electric Tool Corporation", "brand": "Milwaukee®"},
        "MILWAUKEE": {"mfr": "Milwaukee Electric Tool Corporation", "brand": "Milwaukee®"},
        "DIABLO": {"mfr": "Freud Inc", "brand": "Diablo®"},
        "FREUD": {"mfr": "Freud Inc", "brand": "Freud®"},
        "3M": {"mfr": "3M Co", "brand": "3M™"},
        "FRIGIDAIRE": {"mfr": "Rheem Manufacturing", "brand": "FRIGIDAIRE®"},
        "WHIRLPOOL": {"mfr": "Whirlpool Corporation", "brand": "Whirlpool®"},
        "TREX": {"mfr": "Trex Company Inc", "brand": "Trex®"},
        "TIMBERTECH": {"mfr": "TimberTech", "brand": "TimberTech®"},
        "AZEK": {"mfr": "The AZEK Company LLC", "brand": "AZEK®"},
        "MIRKA": {"mfr": "Mirka Abrasives Inc", "brand": "Mirka®"},
        "MAKITA": {"mfr": "Makita Usa Inc", "brand": "Makita®"},
        "VESSEL": {"mfr": "Vessel Tools USA Inc", "brand": "Vessel®"}
    }

    # Known Distributor Co-ops to bypass
    DISTRIBUTOR_COOPS = {
        "APPDE": "Appliance Dealers Cooperative",
        "JAMIN": "Jam Industrial Supply LLC",
        "PARKSITE": "Parksite",
        "BOICA": "Boise Cascade Building Materials",
        "USLUMBER": "U S Lumber"
    }

    @classmethod
    def resolve_brand(cls, clean_supplier: str, desc_text: str, vendor_code: str = "") -> Tuple[str, str, float]:
        """
        Resolves (MANUFACTURER_NAME, BRAND_NAME, confidence)
        """
        desc_upper = desc_text.upper() if desc_text else ""
        supp_upper = clean_supplier.upper() if clean_supplier else ""

        # 1. Check direct keyword match in description first (e.g. 'Milw', 'Diablo', '3M')
        for token, match_data in cls.KNOWN_BRAND_MAP.items():
            # Check whole word boundary
            if f" {token} " in f" {desc_upper} " or desc_upper.startswith(f"{token} ") or desc_upper.startswith(token):
                return match_data["mfr"], match_data["brand"], 0.98

        # 2. Check supplier name if not a distributor co-op
        if vendor_code.upper() not in cls.DISTRIBUTOR_COOPS:
            for token, match_data in cls.KNOWN_BRAND_MAP.items():
                if token in supp_upper:
                    return match_data["mfr"], match_data["brand"], 0.95

        # 3. Fallback: Use cleaned supplier name as Manufacturer if available
        if clean_supplier:
            return clean_supplier, clean_supplier, 0.75

        return "Unbranded", "Unbranded", 0.30
