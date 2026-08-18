import re
from typing import Dict, List, Optional, Tuple


class IngestionNormalizer:
    """
    Cleans raw supplier text, strips placeholders, isolates MPN prefixes,
    and extracts industrial dimension/spec tokens.
    """

    PLACEHOLDER_REGEXES = [
        re.compile(r"^--\s*Unbranded\s*--$", re.IGNORECASE),
        re.compile(r"^--\s*No\s+Unilog\s+Brand\s*--$", re.IGNORECASE),
        re.compile(r"^--\s*No\s+DIB\s+Brand\s*--$", re.IGNORECASE),
        re.compile(r"^--\s*None\s*--$", re.IGNORECASE),
        re.compile(r"^--\s*N/A\s*--$", re.IGNORECASE),
        re.compile(r"^UNKNOWN$", re.IGNORECASE),
        re.compile(r"^UNASSIGNED$", re.IGNORECASE),
        re.compile(r"^\s*$")
    ]

    VENDOR_CODE_REGEX = re.compile(r"^(?P<name>.*?)\s*\((?P<code>[A-Za-z0-9_-]+)\)$")

    @classmethod
    def clean_placeholder(cls, val: Optional[str]) -> str:
        """Returns empty string if value matches any placeholder pattern."""
        if val is None:
            return ""
        stripped = val.strip()
        for pat in cls.PLACEHOLDER_REGEXES:
            if pat.match(stripped):
                return ""
        return stripped

    @classmethod
    def extract_vendor_code(cls, supplier_raw: str) -> Tuple[str, str]:
        """
        Extracts clean supplier name and vendor code:
        'Milwaukee Accessory (4031)' -> ('Milwaukee Accessory', '4031')
        'Jam Industrial Supply LLC (JAMIN)' -> ('Jam Industrial Supply LLC', 'JAMIN')
        """
        if not supplier_raw:
            return "", ""
        match = cls.VENDOR_CODE_REGEX.match(supplier_raw.strip())
        if match:
            return match.group("name").strip(), match.group("code").strip()
        return supplier_raw.strip(), ""

    @classmethod
    def clean_description(cls, part_desc: str, mpn: str) -> str:
        """
        Removes redundant MPN prefix and standardizes escaped quotes and hyphens.
        """
        if not part_desc:
            return ""
        cleaned = part_desc.strip()

        # Standardize double double quotes from CSV: 1/2""x18"" -> 1/2"x18"
        cleaned = cleaned.replace('""', '"')

        # Strip duplicate leading MPN if present
        if mpn and cleaned.startswith(mpn):
            cleaned = cleaned[len(mpn):].lstrip(" ,-_")

        # Clean erroneous 'nx' spacing e.g., '1nx6-16'' -> '1 in x 6 in x 16 ft'
        cleaned = re.sub(r"(\d+(?:/\d+)?)\s*nx\s*", r"\1 in x ", cleaned, flags=re.IGNORECASE)

        return cleaned.strip()

    @classmethod
    def extract_dimension_triplets(cls, text: str) -> List[str]:
        """
        Extracts dimension patterns like: 4-1/2"x.045"x7/8", 5"x.045"x7/8", 1x12-12', 2.75x30
        """
        # Supports whole numbers, decimals, fractions (3/4), and mixed fractions (4-1/2)
        dim_part = r"\d+(?:-\d+/\d+)?(?:\.\d+)?(?:/\d+)?"
        pattern = rf"\b({dim_part}[\"']?\s*[xX]\s*\.?{dim_part}[\"']?(?:\s*[xX]\s*{dim_part}[\"']?)?)\b"
        return [m.strip() for m in re.findall(pattern, text)]
