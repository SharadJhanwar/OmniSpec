from fractions import Fraction
from typing import Optional, Tuple


class DecimalFractionEngine:
    """
    Implements exact 63 inch decimal-to-fraction conversions based on Unilog Decimal_Fraction.xlsx
    Converts values from 1/64 (0.015625) to 63/64 (0.984375).
    """

    # 63 Exact Conversion Lookup
    EXACT_FRACTION_MAP = {
        0.015625: "1/64", 0.03125: "1/32", 0.046875: "3/64", 0.0625: "1/16",
        0.078125: "5/64", 0.09375: "3/32", 0.109375: "7/64", 0.125: "1/8",
        0.140625: "9/64", 0.15625: "5/32", 0.171875: "11/64", 0.1875: "3/16",
        0.203125: "13/64", 0.21875: "7/32", 0.234375: "15/64", 0.25: "1/4",
        0.265625: "17/64", 0.28125: "9/32", 0.296875: "19/64", 0.3125: "5/16",
        0.328125: "21/64", 0.34375: "11/32", 0.359375: "23/64", 0.375: "3/8",
        0.390625: "25/64", 0.40625: "13/32", 0.421875: "27/64", 0.4375: "7/16",
        0.453125: "29/64", 0.46875: "15/32", 0.484375: "31/64", 0.5: "1/2",
        0.515625: "33/64", 0.53125: "17/32", 0.546875: "35/64", 0.5625: "9/16",
        0.578125: "37/64", 0.59375: "19/32", 0.609375: "39/64", 0.625: "5/8",
        0.640625: "41/64", 0.65625: "21/32", 0.671875: "43/64", 0.6875: "11/16",
        0.703125: "45/64", 0.71875: "23/32", 0.734375: "47/64", 0.75: "3/4",
        0.765625: "49/64", 0.78125: "25/32", 0.796875: "51/64", 0.8125: "13/16",
        0.828125: "53/64", 0.84375: "27/32", 0.859375: "55/64", 0.875: "7/8",
        0.890625: "57/64", 0.90625: "29/32", 0.921875: "59/64", 0.9375: "15/16",
        0.953125: "61/64", 0.96875: "31/32", 0.984375: "63/64"
    }

    @classmethod
    def decimal_to_fraction(cls, val: float) -> str:
        """Convert a decimal float (e.g. 50.25) to a standardized fractional string (e.g. 50-1/4)."""
        whole = int(val)
        remainder = round(val - whole, 6)

        if remainder == 0:
            return str(whole)

        # Check exact lookup
        if remainder in cls.EXACT_FRACTION_MAP:
            frac_str = cls.EXACT_FRACTION_MAP[remainder]
        else:
            # Nearest 64th fraction
            frac = Fraction(remainder).limit_denominator(64)
            frac_str = f"{frac.numerator}/{frac.denominator}"

        if whole > 0:
            return f"{whole}-{frac_str}"
        return frac_str

    @classmethod
    def format_dimension_string(cls, val_str: str, uom: str = "in") -> str:
        """Parse raw string like '50.25' or '50-1/4' and return standardized '50-1/4 in'."""
        val_str = val_str.strip()
        try:
            val_float = float(val_str)
            frac_str = cls.decimal_to_fraction(val_float)
            return f"{frac_str} {uom}"
        except ValueError:
            # Already fractional or non-numeric
            return f"{val_str} {uom}"
