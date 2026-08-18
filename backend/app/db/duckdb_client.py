import duckdb
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import process, fuzz
from ..core.config import settings
from ..core.logging import logger


class DuckDBKnowledgeBase:
    """
    High-speed DuckDB In-Memory & Embedded Relational Knowledge Base
    for UniCat 27K Brands, 161K LOVs, Master UOMs, and Deep Category Specs.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or ":memory:"
        self.conn = duckdb.connect(self.db_path)
        self._brand_list_cache: List[Tuple[str, str, str]] = []  # (search_key, mfr_name, brand_name)
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

        # 5. Category Deep Dives: Fittings LOV (Many-to-One Normalization)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS category_fittings_connections (
                raw_variant VARCHAR,
                canonical_value VARCHAR
            );
            CREATE TABLE IF NOT EXISTS category_fittings_materials (
                raw_material VARCHAR,
                canonical_material VARCHAR
            );
            CREATE TABLE IF NOT EXISTS category_fittings_types (
                fitting_type VARCHAR,
                source_url VARCHAR
            );
        """)

        # 6. Category Deep Dives: Faucets LOV
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS category_faucets_lov (
                attribute_label VARCHAR,
                sequence_order INTEGER,
                permitted_values VARCHAR,
                synonyms VARCHAR
            );
        """)

    def load_seed_data(self):
        """Populate initial seed knowledge into DuckDB tables."""
        logger.info("Seeding Master Knowledge Base into DuckDB...")

        # 1. Seed Decimal Fractions (63 exact inch conversions)
        from ..services.decimal_fraction import DecimalFractionEngine
        fraction_data = []
        for dec, frac in DecimalFractionEngine.EXACT_FRACTION_MAP.items():
            fraction_data.append((dec, frac, f"{frac} in"))
        self.conn.executemany("INSERT INTO decimal_fractions VALUES (?, ?, ?)", fraction_data)

        # 2. Seed Master UOM Standards
        from ..services.uom_converter import UOMConverter
        uom_data = []
        for raw, app in UOMConverter.CANONICAL_UOM_MAP.items():
            uom_data.append((raw, app, "General", f"Number + ' {app}'", f"24 {app}"))
        self.conn.executemany("INSERT INTO master_uom VALUES (?, ?, ?, ?, ?)", uom_data)

        # 3. Seed Core UniCat Brands (27k representative master seed)
        core_brands = [
            ("Rheem Manufacturing", "RHEEM", "FRIGIDAIRE®", "FRIG", "FRIGIDAIRE", True, "®"),
            ("Whirlpool Corporation", "WHIRL", "Whirlpool®", "WHIRL", "WHIRLPOOL", True, "®"),
            ("Milwaukee Electric Tool Corporation", "MILW", "Milwaukee®", "MILW", "MILWAUKEE", True, "®"),
            ("Freud Inc", "FREUD", "Diablo®", "DIAB", "DIABLO", True, "®"),
            ("Freud Inc", "FREUD", "Freud®", "FREUD", "FREUD", True, "®"),
            ("3M Co", "3M", "3M™", "3M", "3M", True, "™"),
            ("3M Co", "3M", "Cubitron™ II", "CUB", "CUBITRON", True, "™"),
            ("Trex Company Inc", "TREX", "Trex®", "TREX", "TREX", True, "®"),
            ("TimberTech", "TIMB", "TimberTech®", "TIMB", "TIMBERTECH", True, "®"),
            ("The AZEK Company LLC", "AZEK", "AZEK®", "AZEK", "AZEK", True, "®"),
            ("Mirka Abrasives Inc", "MIRKA", "Mirka®", "MIRKA", "MIRKA", True, "®"),
            ("Makita Usa Inc", "MAK", "Makita®", "MAK", "MAKITA", True, "®"),
            ("Vessel Tools USA Inc", "VES", "Vessel®", "VES", "VESSEL", True, "®"),
            ("Jam Industrial Supply LLC", "JAMIN", "Jam Industrial Supply", "JAMIN", "JAM INDUSTRIAL", False, ""),
            ("Boise Cascade Building Materials", "BOICA", "Boise Cascade", "BOICA", "BOISE CASCADE", False, ""),
            ("Parksite", "PARK", "Parksite", "PARK", "PARKSITE", False, "")
        ]
        self.conn.executemany("INSERT INTO unicat_brands VALUES (?, ?, ?, ?, ?, ?, ?)", core_brands)

        # 4. Seed Fittings Many-to-One Normalizations
        fittings_connections = [
            ("MNPT", "MNPT"), ("MIP", "MNPT"), ("Male NPT", "MNPT"), ("Male Pipe Thread", "MNPT"),
            ("FNPT", "FNPT"), ("FIP", "FNPT"), ("Female NPT", "FNPT"), ("Female Pipe Thread", "FNPT"),
            ("Compression", "Compression"), ("Comp", "Compression"), ("Flange", "Flanged"), ("Flanged", "Flanged"),
            ("Push-to-Connect", "Push-to-Connect"), ("Push-Fit", "Push-to-Connect"), ("SharkBite", "Push-to-Connect"),
            ("Socket Weld", "Socket Weld"), ("Threaded", "Threaded"), ("Crimp", "Crimp")
        ]
        self.conn.executemany("INSERT INTO category_fittings_connections VALUES (?, ?)", fittings_connections)

        fittings_materials = [
            ("BRS", "Brass"), ("Brass", "Brass"), ("Forged Brass", "Brass"), ("Lead Free Brass", "Lead-Free Brass"),
            ("SST", "Stainless Steel"), ("Stainless", "Stainless Steel"), ("304 SS", "Stainless Steel"), ("316 SS", "Stainless Steel"),
            ("PVC", "PVC"), ("Polyvinyl Chloride", "PVC"), ("CPVC", "CPVC"),
            ("Copper", "Copper"), ("Cast Bronze", "Bronze"), ("Ductile Iron", "Ductile Iron"),
            ("Carbon Steel", "Carbon Steel"), ("Malleable Iron", "Malleable Iron")
        ]
        self.conn.executemany("INSERT INTO category_fittings_materials VALUES (?, ?)", fittings_materials)

        # 5. Seed UniCat LOV Classpath Schemas
        lov_schema_seeds = [
            # Dishwashers
            ("Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "Built-In Dishwashers", "Y", "Series", "Professional Series, Eco Series, Gallery Series", "Series", "Professional Series|Eco Series|Gallery Series", "", "Approved Series list"),
            ("Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "Built-In Dishwashers", "Y", "Number of Wash Cycles", "3, 4, 5, 6, 7, 8", "Number of Wash Cycles", "3|4|5|6|7|8", "", "Must be integer"),
            ("Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "Built-In Dishwashers", "Y", "Voltage Rating", "120, 240", "Voltage Rating", "120|240", "V", "Capture integer, UOM V"),
            ("Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "Built-In Dishwashers", "Y", "Amperage Rating", "10, 15, 20", "Amperage Rating", "10|15|20", "A", "Capture integer, UOM A"),
            ("Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "Built-In Dishwashers", "Y", "Mounting Type", "Built-in, Leg, Under-Counter", "Mounting Type", "Built-in|Leg", "", "Mounting position"),
            ("Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "Built-In Dishwashers", "Y", "Sound Level", "41, 44, 47, 50, 52", "Sound Level", "41|44|47|50|52", "dBA", "Sound level in dBA"),
            ("Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers", "Built-In Dishwashers", "Y", "Material", "Stainless Steel, Plastic", "Material", "Stainless Steel|Plastic", "", "Tub material"),

            # Cut-Off Wheels
            ("Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels", "Cut-Off Wheels", "Y", "Diameter", "4-1/2, 5, 6, 7, 9, 12, 14", "Diameter", "4-1/2|5|6|7|9|12|14", "in", "Wheel diameter in inches"),
            ("Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels", "Cut-Off Wheels", "Y", "Thickness", ".040, .045, 1/16, 3/32, 7/64, 1/8", "Thickness", ".040|.045|1/16|3/32|7/64|1/8", "in", "Wheel thickness"),
            ("Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels", "Cut-Off Wheels", "Y", "Arbor Size", "5/8, 7/8, 1, 20mm, 5/8-11", "Arbor Size", "5/8|7/8|1|20 mm|5/8-11", "in", "Arbor hole dimension"),
            ("Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels", "Cut-Off Wheels", "Y", "Abrasive Material", "Aluminum Oxide, Silicon Carbide, Ceramic", "Abrasive Material", "Aluminum Oxide|Silicon Carbide|Ceramic", "", "Grain type"),

            # Decking Boards
            ("Building Materials>Decking & Railing>Decking Boards", "Decking Boards", "Y", "Series", "Enhance Basics, Enhance Naturals, Select 2.0, Lineage", "Series", "Enhance Basics|Enhance Naturals|Select 2.0|Lineage", "", "Product series"),
            ("Building Materials>Decking & Railing>Decking Boards", "Decking Boards", "Y", "Edge Profile", "Grooved, Square Edge", "Edge Profile", "Grooved|Square Edge", "", "Board profile"),
            ("Building Materials>Decking & Railing>Decking Boards", "Decking Boards", "Y", "Color", "Honey Grove, Tide Pool, Cinnamon Cove, Golden Hour, Pebble Beach, Malted Barley, Biscayne", "Color", "Honey Grove|Tide Pool|Cinnamon Cove|Golden Hour|Pebble Beach|Malted Barley|Biscayne", "", "Manufacturer color name")
        ]
        self.conn.executemany("INSERT INTO unicat_lov VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", lov_schema_seeds)

        # Build in-memory fast search cache
        self._refresh_brand_cache()
        logger.info("Master Knowledge Base seeding complete.")

    def _refresh_brand_cache(self):
        rows = self.conn.execute("SELECT search_alias, manufacturer_name, brand_name FROM unicat_brands").fetchall()
        self._brand_list_cache = [(r[0], r[1], r[2]) for r in rows]

    def find_brand(self, query: str) -> Optional[Tuple[str, str, float]]:
        """Fuzzy search for manufacturer & brand using RapidFuzz over UniCat cache."""
        if not query or not self._brand_list_cache:
            return None

        q_clean = query.strip().upper()
        # Direct exact match
        for alias, mfr, brand in self._brand_list_cache:
            if alias == q_clean or alias in q_clean or q_clean in alias:
                return mfr, brand, 0.98

        # Fuzzy match
        choices = [item[0] for item in self._brand_list_cache]
        match = process.extractOne(q_clean, choices, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= 80:
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


# Singleton Knowledge Base Instance
kb = DuckDBKnowledgeBase()
kb.load_seed_data()
