import time
import re
from typing import Dict, Any, Tuple
from ..schemas.state_schema import ProductEnrichmentState, AgentTrace
from ..db.duckdb_client import kb
from ..core.logging import logger


class TaxonomyClassifierAgent:
    """
    Agent 3: Taxonomy, UNSPSC & Classpath Classifier Agent
    Maps product tokens into the 4-tier UniCat taxonomy hierarchy,
    assigns 8-digit UNSPSC codes, and triggers dynamic LOV schemas.
    """

    # Comprehensive Classification Taxonomy Rules
    TAXONOMY_RULES = [
        # Dishwashers
        {
            "match": lambda desc, mpn: "DISHWASHER" in desc or mpn.startswith("PDSH") or mpn.startswith("WDTS"),
            "classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
            "dept": "Appliances",
            "class": "Large Appliances",
            "fine": "Dishwashers",
            "product_name": "Dishwasher",
            "unspsc": "52141505"
        },
        # Cut-Off Discs & Grinding Wheels
        {
            "match": lambda desc, mpn: ("CUT OFF" in desc or "CUT-OFF" in desc or "GRIND" in desc) and "DISC" in desc or "WHEEL" in desc,
            "classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels",
            "dept": "Abrasives",
            "class": "Abrasive Wheels",
            "fine": "Cut-Off Discs",
            "product_name": "Metal Cut-Off Disc",
            "unspsc": "31191500"
        },
        # Sanding Belts
        {
            "match": lambda desc, mpn: "SANDING BELT" in desc or "BELT" in desc and ("GRIT" in desc or "SANDING" in desc),
            "classpath": "Abrasives & Polishing>Sandpaper & Abrasive Pads>Sanding Belts",
            "dept": "Abrasives",
            "class": "Abrasive Belts",
            "fine": "Sanding Belts",
            "product_name": "Sanding Belt",
            "unspsc": "31191500"
        },
        # Sanding Discs / Film Discs
        {
            "match": lambda desc, mpn: ("STIKIT" in desc or "ABRANET" in desc or "HIOLIT" in desc or "DISC" in desc) and ("FILM" in desc or "GRIT" in desc or "P150" in desc or "P80" in desc or "P120" in desc or "P180" in desc or "P220" in desc or "P320" in desc),
            "classpath": "Abrasives & Polishing>Sandpaper & Abrasive Pads>Sanding Discs",
            "dept": "Abrasives",
            "class": "Abrasive Discs",
            "fine": "Film Discs",
            "product_name": "Sanding Disc",
            "unspsc": "31191500"
        },
        # Sanding Sponges
        {
            "match": lambda desc, mpn: "SPONGE" in desc and "SANDING" in desc,
            "classpath": "Abrasives & Polishing>Sandpaper & Abrasive Pads>Sanding Sponges & Blocks",
            "dept": "Abrasives",
            "class": "Abrasive Sponges",
            "fine": "Sanding Sponges",
            "product_name": "Sanding Sponge",
            "unspsc": "31191500"
        },
        # Fascia Boards
        {
            "match": lambda desc, mpn: "FASCIA" in desc or "PVC FASCIA" in desc,
            "classpath": "Building Materials>Decking & Railing>Fascia Boards",
            "dept": "Building Materials",
            "class": "Decking",
            "fine": "Fascia Boards",
            "product_name": "Fascia Board",
            "unspsc": "30103600"
        },
        # Decking Boards
        {
            "match": lambda desc, mpn: "DECKING" in desc or "TREX" in desc and ("GROOVED" in desc or "SQ EDGE" in desc or "SQUARE EDGE" in desc),
            "classpath": "Building Materials>Decking & Railing>Decking Boards",
            "dept": "Building Materials",
            "class": "Decking",
            "fine": "Composite Decking",
            "product_name": "Decking Board",
            "unspsc": "30103600"
        },
        # Pipe & Tube Fittings
        {
            "match": lambda desc, mpn: "CPLG" in desc or "COUPLING" in desc or "ELBOW" in desc or "TEE" in desc or "ADAPTER" in desc or "FITTING" in desc,
            "classpath": "Plumbing>Pipe, Tube & Hose Fittings>Pipe Fittings",
            "dept": "Plumbing",
            "class": "Fittings",
            "fine": "Pipe Fittings",
            "product_name": "Pipe Coupling",
            "unspsc": "40171500"
        },
        # Kitchen & Bath Faucets
        {
            "match": lambda desc, mpn: "FAUCET" in desc or "SINK FAUCET" in desc,
            "classpath": "Plumbing>Commercial & Residential Faucets>Kitchen Sink Faucets",
            "dept": "Plumbing",
            "class": "Faucets",
            "fine": "Kitchen Faucets",
            "product_name": "Kitchen Sink Faucet",
            "unspsc": "30181702"
        },
        # Screwdriver / Driver Bits
        {
            "match": lambda desc, mpn: "SCREWDRIVER" in desc or "BIT SET" in desc or "DRIVE BIT" in desc or "SCREW SETTER" in desc,
            "classpath": "Tools & Hardware>Fasteners & Screwdriving>Driver Bits",
            "dept": "Hardware",
            "class": "Fasteners",
            "fine": "Bits",
            "product_name": "Driver Bit",
            "unspsc": "27112814"
        }
    ]

    @classmethod
    def execute(cls, state: ProductEnrichmentState) -> Dict[str, Any]:
        t0 = time.perf_counter()

        desc_upper = (state.cleaned_part_desc or "").upper()
        mpn_upper = (state.clean_mfg_part_num or "").upper()

        matched_rule = None
        for rule in cls.TAXONOMY_RULES:
            if rule["match"](desc_upper, mpn_upper):
                matched_rule = rule
                break

        if matched_rule:
            classpath = matched_rule["classpath"]
            dept = matched_rule["dept"]
            class_name = matched_rule["class"]
            fine = matched_rule["fine"]
            product_name = matched_rule["product_name"]
            unspsc = matched_rule["unspsc"]
            conf = 0.98
        else:
            # Fallback General Classification
            classpath = "Industrial Supplies & Hardware>General Hardware"
            dept = "Hardware"
            class_name = "General"
            fine = "Industrial Hardware"
            product_name = "Industrial Component"
            unspsc = "31160000"
            conf = 0.60

        # Retrieve active LOV attribute schema from DuckDB
        active_lov_schema = kb.get_lov_schema(classpath)

        trace = AgentTrace(
            agent_name="Agent 3: Taxonomy & Classification",
            execution_time_ms=round((time.perf_counter() - t0) * 1000, 2),
            notes=[
                f"Assigned Classpath: '{classpath}' [UNSPSC: {unspsc}]",
                f"Product Name: '{product_name}'",
                f"Loaded {len(active_lov_schema)} active LOV schema attributes"
            ],
            extracted_data={
                "classpath": classpath,
                "dept": dept,
                "class_name": class_name,
                "fine": fine,
                "product_name": product_name,
                "unspsc": unspsc,
                "active_schema_count": len(active_lov_schema)
            }
        )

        return {
            "classpath": classpath,
            "dept": dept,
            "class_name": class_name,
            "fine": fine,
            "product_name": product_name,
            "unspsc": unspsc,
            "taxonomy_confidence": conf,
            "traces": state.traces + [trace]
        }
