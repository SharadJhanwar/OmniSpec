import re
from typing import Optional, Dict


class UOMConverter:
    """
    Enforces the Unilog Master UOM Standards (~500 approved abbreviations across 89 types)
    and validates mandatory single-space formatting (e.g. '24 in', '120 V', '15 A').
    """

    # Canonical Unit Mapping (Normalizing variants to single approved standard)
    CANONICAL_UOM_MAP = {
        # Length / Dimensions
        "inches": "in", "inch": "in", "in.": "in", "in": "in", "\"": "in",
        "feet": "ft", "foot": "ft", "ft.": "ft", "ft": "ft", "'": "ft",
        "yard": "yd", "yards": "yd", "yd.": "yd", "yd": "yd",
        "millimeter": "mm", "millimeters": "mm", "mm.": "mm", "mm": "mm",
        "centimeter": "cm", "centimeters": "cm", "cm.": "cm", "cm": "cm",
        "meter": "m", "meters": "m", "m.": "m", "m": "m",

        # Electrical
        "volts": "V", "volt": "V", "v.": "V", "v": "V", "vac": "VAC", "vdc": "VDC",
        "amperes": "A", "ampere": "A", "amps": "A", "amp": "A", "a.": "A", "a": "A",
        "watts": "W", "watt": "W", "w.": "W", "w": "W",
        "kilowatts": "kW", "kilowatt": "kW", "kw": "kW",
        "kilowatt-hour": "kW-hr", "kwh": "kW-hr", "kw-hr": "kW-hr", "kw-hrs": "kW-hr",
        "hertz": "Hz", "hz": "Hz",

        # Acoustic
        "decibels": "dBA", "decibel": "dBA", "dba": "dBA", "db": "dBA",

        # Weight
        "pounds": "lb", "pound": "lb", "lbs.": "lb", "lbs": "lb", "lb.": "lb", "lb": "lb",
        "ounces": "oz", "ounce": "oz", "oz.": "oz", "oz": "oz",
        "kilograms": "kg", "kilogram": "kg", "kg.": "kg", "kg": "kg",
        "grams": "g", "gram": "g", "g.": "g", "g": "g",

        # Flow / Speed / Volume
        "gallons per minute": "gpm", "gpm": "gpm",
        "revolutions per minute": "rpm", "rpm": "rpm",
        "cubic feet per minute": "cfm", "cfm": "cfm",
        "gallons": "gal", "gallon": "gal", "gal": "gal",

        # Packaging / Quantity
        "each": "Each", "ea": "Each", "pk": "Pack", "pack": "Pack",
        "box": "Box", "bx": "Box", "bag": "Bag", "bg": "Bag",
        "carton": "Carton", "ctn": "Carton", "case": "Case", "cs": "Case",
        "pair": "Pair", "pr": "Pair", "set": "Set", "roll": "Roll", "rl": "Roll"
    }

    @classmethod
    def normalize_uom(cls, raw_uom: str) -> str:
        """Map raw UOM variant to approved Unilog abbreviation."""
        if not raw_uom:
            return ""
        clean = raw_uom.strip().lower()
        return cls.CANONICAL_UOM_MAP.get(clean, raw_uom.strip())

    @classmethod
    def ensure_uom_spacing(cls, text: str) -> str:
        """
        Ensures a single space between number and approved unit:
        '24in' -> '24 in', '120V' -> '120 V', '15A' -> '15 A', '47dBA' -> '47 dBA'
        """
        if not text:
            return ""

        # Pattern: Number (integer, fraction, decimal) directly touching a unit
        pattern = r"(\d+(?:[/-]\d+)?(?:\.\d+)?)\s*(in|ft|mm|cm|yd|V|A|W|kW|kW-hr|Hz|dBA|lb|oz|kg|g|gpm|rpm|cfm)\b"
        return re.sub(pattern, r"\1 \2", text, flags=re.IGNORECASE)
