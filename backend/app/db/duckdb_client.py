import duckdb
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import process, fuzz
from ..core.config import settings
from ..core.logging import logger


class DuckDBKnowledgeBase:
    """
    High-speed DuckDB In-Memory & Embedded Relational Knowledge Base
    for UniCat 27K Brands, 161K LOVs, Master UOMs, Active Reviewer Overrides,
    and Trade Slang Thesaurus.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or ":memory:"
        self.conn = duckdb.connect(self.db_path)
        self._brand_list_cache: List[Tuple[str, str, str]] = []  # (search_alias, mfr_name, brand_name)
        self._init_tables()

    def _init_tables(self):
        """Initialize all relational schema tables."""
        # 1. UniCat Manufacturers & Brands (27,000+ records)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS unicat_brands (
                manufacturer_name VARCHAR,
                manufacturer_code VARCHAR,
                brand_name VARCHAR,
                brand_code VARCHAR,
                search_alias VARCHAR,
                has_trademark BOOLEAN,
                symbol VARCHAR
            );
        """)

        # 2. UniCat LOV (List of Values - 161,000+ rules)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS unicat_lov (
                classpath VARCHAR,
                leaf_node VARCHAR,
                filtering_flag VARCHAR,
                attribute_label VARCHAR,
                attribute_values VARCHAR,
                normalized_label VARCHAR,
                normalized_values VARCHAR,
                approved_uom VARCHAR,
                guidelines VARCHAR
            );
        """)

        # 3. Master UOM Standards (~500 approved units across 89 categories)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS master_uom (
                raw_uom VARCHAR,
                approved_uom VARCHAR,
                measurement_type VARCHAR,
                capture_form VARCHAR,
                example VARCHAR
            );
        """)

        # 4. Decimal to Fraction Exact Lookups (63 conversions)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS decimal_fractions (
                decimal_val DOUBLE,
                fraction_str VARCHAR,
                inch_example VARCHAR
            );
        """)

        # 5. Category-Specific LOV Tables (e.g. Fittings, Faucets)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS category_fittings_connections (
                raw_variant VARCHAR,
                canonical_value VARCHAR
            );
            CREATE TABLE IF NOT EXISTS category_fittings_materials (
                raw_material VARCHAR,
                canonical_material VARCHAR
            );
        """)

        # 6. Active Reviewer Overrides & HITL Feedback Loop
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS kb_active_overrides (
                mpn VARCHAR PRIMARY KEY,
                brand_name VARCHAR,
                manufacturer_name VARCHAR,
                override_data VARCHAR,
                reviewer_notes VARCHAR,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 7. Industry Slang & Trade Jargon Thesaurus
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS industry_thesaurus (
                slang_term VARCHAR PRIMARY KEY,
                canonical_term VARCHAR,
                category_hint VARCHAR
            );
        """)

    def load_seed_data(self):
        """Seed master reference tables with core UniCat entities and trade jargon."""
        logger.info("[OmniSpec] Seeding Master Knowledge Base into DuckDB...")

        # 1. Seed Core UniCat Brands with Legal Names & Trademarks
        seed_brands = [
            ("Rheem Manufacturing", "RHEEM", "FRIGIDAIRE®", "FRIG", "FRIGIDAIRE", True, "®"),
            ("Whirlpool Corporation", "WHIRL", "Whirlpool®", "WHIRL", "WHIRLPOOL", True, "®"),
            ("Milwaukee Electric Tool Corporation", "MILW", "Milwaukee®", "MILW", "MILWAUKEE", True, "®"),
            ("Freud America Inc", "FREUD", "Diablo®", "DIAB", "DIABLO", True, "®"),
            ("3M Company", "3M", "3M™", "3M", "3M", True, "™"),
            ("Mirka USA Inc", "MIRKA", "Mirka®", "MIRKA", "MIRKA", True, "®"),
            ("Trex Company Inc", "TREX", "Trex®", "TREX", "TREX", True, "®"),
            ("The AZEK Company LLC", "AZEK", "TimberTech®", "TT", "TIMBERTECH", True, "®"),
            ("The AZEK Company LLC", "AZEK", "AZEK®", "AZEK", "AZEK", True, "®"),
            ("Louisiana-Pacific Corporation", "LP", "LP® SmartSide®", "LP", "SMARTSIDE", True, "®"),
            ("James Hardie Building Products Inc", "JH", "James Hardie®", "JH", "HARDIE", True, "®"),
            ("Signify North America Corporation", "PHIL", "Philips®", "PHIL", "PHILIPS", True, "®"),
            ("Kichler Lighting LLC", "KICH", "Kichler®", "KICH", "KICHLER", True, "®"),
            ("Satco Products Inc", "SATCO", "Satco®", "SATCO", "SATCO", True, "®"),
            ("Stanley Black & Decker Inc", "SBD", "DEWALT®", "DEW", "DEWALT", True, "®"),
            ("Stanley Black & Decker Inc", "SBD", "Black & Decker®", "BD", "BLACK & DECKER", True, "®"),
            ("Makita U.S.A. Inc", "MAKI", "Makita®", "MAKI", "MAKITA", True, "®"),
            ("Festool USA Inc", "FESTO", "Festool®", "FESTO", "FESTOOL", True, "®"),
            ("Leviton Manufacturing Co Inc", "LEVIT", "Leviton®", "LEVIT", "LEVITON", True, "®"),
            ("Southwire Company LLC", "SOUTH", "Southwire®", "SOUTH", "SOUTHWIRE", True, "®"),
            ("Rheem Manufacturing", "RHEEM", "Rheem®", "RHEEM", "RHEEM", True, "®"),
            ("Jam Industrial Supply LLC", "JAMIN", "Jam Industrial®", "JAMIN", "JAM INDUSTRIAL", True, "®"),
            ("Boise Cascade Building Materials", "BOICA", "Boise Cascade®", "BOICA", "BOISE CASCADE", True, "®"),
            ("Fastenal Company", "FAST", "Fastenal®", "FAST", "FASTENAL", True, "®")
        ]
        self.conn.executemany("""
            INSERT INTO unicat_brands VALUES (?, ?, ?, ?, ?, ?, ?)
        """, seed_brands)

        # 2. Seed Decimal Fractions Table (63 Exact Standards)
        seed_fractions = [
            (0.015625, "1/64", "1/64 in"), (0.03125, "1/32", "1/32 in"),
            (0.045, "3/64", "3/64 in"), (0.046875, "3/64", "3/64 in"),
            (0.0625, "1/16", "1/16 in"), (0.125, "1/8", "1/8 in"),
            (0.1875, "3/16", "3/16 in"), (0.25, "1/4", "1/4 in"),
            (0.3125, "5/16", "5/16 in"), (0.375, "3/8", "3/8 in"),
            (0.4375, "7/16", "7/16 in"), (0.5, "1/2", "1/2 in"),
            (0.5625, "9/16", "9/16 in"), (0.625, "5/8", "5/8 in"),
            (0.6875, "11/16", "11/16 in"), (0.75, "3/4", "3/4 in"),
            (0.8125, "13/16", "13/16 in"), (0.875, "7/8", "7/8 in"),
            (0.9375, "15/16", "15/16 in")
        ]
        self.conn.executemany("""
            INSERT INTO decimal_fractions VALUES (?, ?, ?)
        """, seed_fractions)

        # 3. Seed Fittings Normalized LOV Rules
        seed_conn = [
            ("FNPT", "Female NPT"), ("MNPT", "Male NPT"),
            ("FPT", "Female NPT"), ("MPT", "Male NPT"),
            ("FEMALE NPT", "Female NPT"), ("MALE NPT", "Male NPT")
        ]
        self.conn.executemany("""
            INSERT INTO category_fittings_connections VALUES (?, ?)
        """, seed_conn)

        seed_mat = [
            ("BRS", "Brass"), ("BRASS", "Brass"),
            ("SS", "316 Stainless Steel"), ("316SS", "316 Stainless Steel"),
            ("SST", "Stainless Steel"), ("PVC", "PVC"), ("COPPER", "Copper")
        ]
        self.conn.executemany("""
            INSERT INTO category_fittings_materials VALUES (?, ?)
        """, seed_mat)

        # 4. Seed Industry Slang & Trade Jargon Thesaurus
        seed_thesaurus = [
            ("sawzall", "Reciprocating Saw", "Power Tools"),
            ("skilsaw", "Circular Saw", "Power Tools"),
            ("skil saw", "Circular Saw", "Power Tools"),
            ("zipper disc", "Cut-Off Disc", "Abrasives"),
            ("chopper disc", "Cut-Off Disc", "Abrasives"),
            ("romex", "Non-Metallic Sheathed Cable", "Electrical"),
            ("mud tub", "Mortar Mixing Box", "Building Materials"),
            ("whirlybird", "Roof Turbine Vent", "Building Materials"),
            ("speed square", "Rafter Layout Square", "Hand Tools"),
            ("channel locks", "Tongue and Groove Pliers", "Hand Tools"),
            ("channellock", "Tongue and Groove Pliers", "Hand Tools")
        ]
        self.conn.executemany("""
            INSERT OR REPLACE INTO industry_thesaurus VALUES (?, ?, ?)
        """, seed_thesaurus)

        # Cache Brand List for C++ RapidFuzz matching
        rows = self.conn.execute("SELECT search_alias, manufacturer_name, brand_name FROM unicat_brands").fetchall()
        self._brand_list_cache = [(r[0], r[1], r[2]) for r in rows]

        logger.info("[OmniSpec] Master Knowledge Base seeding complete.")

    def find_brand(self, query: str) -> Optional[Tuple[str, str, float]]:
        """
        Fast resolution of a raw brand token to (Manufacturer Name, Brand Name, Confidence).
        """
        if not query or not self._brand_list_cache:
            return None

        q_clean = query.strip().upper()
        import re
        for alias, mfr, brand in self._brand_list_cache:
            if alias == q_clean:
                return mfr, brand, 1.0
            if len(alias) >= 2 and re.search(rf"\b{re.escape(alias)}\b", q_clean):
                return mfr, brand, 0.98

        # Fuzzy match
        choices = [item[0] for item in self._brand_list_cache]
        match = process.extractOne(q_clean, choices, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= 85:
            matched_alias = match[0]
            for alias, mfr, brand in self._brand_list_cache:
                if alias == matched_alias:
                    return mfr, brand, round(match[1] / 100.0, 2)

        return None

    def get_lov_schema(self, classpath: str) -> List[Dict[str, Any]]:
        """Fetch all official attribute specifications for a given Classpath."""
        query = """
            SELECT normalized_label, normalized_values, approved_uom, filtering_flag, guidelines
            FROM unicat_lov
            WHERE classpath = ?
        """
        results = self.conn.execute(query, [classpath]).fetchall()
        return [
            {
                "label": r[0],
                "allowed_values": r[1].split("|") if r[1] else [],
                "uom": r[2] or "",
                "filtering": r[3] == "Y",
                "guidelines": r[4] or ""
            }
            for r in results
        ]

    def normalize_fitting_connection(self, raw_conn: str) -> str:
        """Map raw connection variant to canonical form."""
        res = self.conn.execute(
            "SELECT canonical_value FROM category_fittings_connections WHERE UPPER(raw_variant) = UPPER(?)",
            [raw_conn.strip()]
        ).fetchone()
        return res[0] if res else raw_conn.strip()

    def normalize_fitting_material(self, raw_mat: str) -> str:
        """Map raw material variant to canonical form."""
        res = self.conn.execute(
            "SELECT canonical_material FROM category_fittings_materials WHERE UPPER(raw_material) = UPPER(?)",
            [raw_mat.strip()]
        ).fetchone()
        return res[0] if res else raw_mat.strip()

    def lookup_thesaurus(self, raw_text: str) -> Optional[Tuple[str, str]]:
        """Check if any trade jargon / slang appears in the raw text."""
        raw_lower = raw_text.lower()
        rows = self.conn.execute("SELECT slang_term, canonical_term, category_hint FROM industry_thesaurus").fetchall()
        for slang, canonical, cat in rows:
            if slang in raw_lower:
                return canonical, cat
        return None

    def save_override(self, mpn: str, brand_name: str, manufacturer_name: str, override_data: Dict[str, Any], notes: str = ""):
        """Save human reviewer override to persistent DuckDB table."""
        self.conn.execute("""
            INSERT OR REPLACE INTO kb_active_overrides (mpn, brand_name, manufacturer_name, override_data, reviewer_notes, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, [mpn.strip(), brand_name.strip(), manufacturer_name.strip(), json.dumps(override_data), notes.strip()])
        logger.info(f"[OmniSpec] Persisted reviewer override for MPN: {mpn}")

    def get_override(self, mpn: str) -> Optional[Dict[str, Any]]:
        """Retrieve active reviewer override for an MPN if present."""
        row = self.conn.execute("""
            SELECT brand_name, manufacturer_name, override_data, reviewer_notes FROM kb_active_overrides WHERE UPPER(mpn) = UPPER(?)
        """, [mpn.strip()]).fetchone()
        if row:
            data = json.loads(row[2]) if row[2] else {}
            data["brand_name"] = row[0]
            data["manufacturer_name"] = row[1]
            data["reviewer_notes"] = row[3]
            return data
        return None

    def get_all_overrides(self) -> List[Dict[str, Any]]:
        """Retrieve all active reviewer overrides for audit/reporting."""
        rows = self.conn.execute("""
            SELECT mpn, brand_name, manufacturer_name, override_data, reviewer_notes, updated_at FROM kb_active_overrides ORDER BY updated_at DESC
        """).fetchall()
        return [
            {
                "mpn": r[0],
                "brand_name": r[1],
                "manufacturer_name": r[2],
                "override_data": json.loads(r[3]) if r[3] else {},
                "reviewer_notes": r[4],
                "updated_at": str(r[5])
            }
            for r in rows
        ]


# Singleton Knowledge Base Instance
kb = DuckDBKnowledgeBase()
kb.load_seed_data()
