import time
from family_clusterer import OfflineFamilyClusterer

TEST_CATALOG = [
    # Family 1: DEWALT DCG413 Grinder Series
    {
        "Mfg_Part_Num": "DCG413B",
        "BRAND_NAME": "DEWALT",
        "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders",
        "SHORT_DESC": "DEWALT 20V MAX XR 4-1/2 in Brushless Angle Grinder (Tool Only)"
    },
    {
        "Mfg_Part_Num": "DCG413P2",
        "BRAND_NAME": "DEWALT",
        "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders",
        "SHORT_DESC": "DEWALT 20V MAX XR 4-1/2 in Brushless Angle Grinder Kit (2x 5.0Ah Batteries)"
    },
    {
        "Mfg_Part_Num": "DCG413R2",
        "BRAND_NAME": "DEWALT",
        "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders",
        "SHORT_DESC": "DEWALT 20V/60V MAX FlexVolt 4-1/2 in Grinder Kit (2x 6.0Ah Batteries)"
    },

    # Family 2: Bosch 800 Series Dishwashers (Color Variations)
    {
        "Mfg_Part_Num": "SHX78B75UC",
        "BRAND_NAME": "Bosch",
        "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
        "SHORT_DESC": "Bosch 800 Series 24 in Built-In Dishwasher Stainless Steel 42 dBA"
    },
    {
        "Mfg_Part_Num": "SHX78B76UC",
        "BRAND_NAME": "Bosch",
        "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
        "SHORT_DESC": "Bosch 800 Series 24 in Built-In Dishwasher Black Stainless Steel 42 dBA"
    },

    # Family 3: Mueller Brass Couplings with Assortment Gap (1/4, 3/8, 3/4 -> Missing 1/2)
    {
        "Mfg_Part_Num": "CPLG-14-BRS",
        "BRAND_NAME": "Mueller",
        "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings",
        "SHORT_DESC": "Mueller 1/4 in Brass Pipe Coupling 150# NPT Threaded"
    },
    {
        "Mfg_Part_Num": "CPLG-38-BRS",
        "BRAND_NAME": "Mueller",
        "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings",
        "SHORT_DESC": "Mueller 3/8 in Brass Pipe Coupling 150# NPT Threaded"
    },
    {
        "Mfg_Part_Num": "CPLG-34-BRS",
        "BRAND_NAME": "Mueller",
        "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings",
        "SHORT_DESC": "Mueller 3/4 in Brass Pipe Coupling 150# NPT Threaded"
    }
]


def run_clustering_benchmark():
    print("=" * 65)
    print("[BENCHMARK] PRODUCT FAMILY DISCOVERY & ASSORTMENT GAP DETECTOR")
    print("=" * 65)

    start_time = time.perf_counter()
    families = OfflineFamilyClusterer.discover_families(TEST_CATALOG)
    exec_ms = (time.perf_counter() - start_time) * 1000

    print(f"Discovered {len(families)} Parent Product Families across {len(TEST_CATALOG)} SKUs in {exec_ms:.3f} ms:\n")

    for idx, fam in enumerate(families, 1):
        print(f"Family {idx}: {fam['family_name']} ({fam['total_variants']} child SKUs)")
        print(f"  * Base Series MPN: {fam['base_series_mpn']}")
        print(f"  * Variant Axes   : {[ax['name'] + ' -> ' + str(ax['values']) for ax in fam['variant_axes']]}")
        print("  * Child Matrix   :")
        for v in fam['variants']:
            print(f"    - {v['mpn']}: {v['axis_values']}")
        
        if fam['detected_gaps']:
            print(f"  * [GAP WARNING] Detected Assortment Gaps ({len(fam['detected_gaps'])}):")
            for gap in fam['detected_gaps']:
                print(f"    - [{gap['confidence_level']}] Missing: {gap['missing_sizes']} in sequence (Present: {gap['present_sizes']})")
                print(f"      Evidence: {gap['evidence_notes']}")
        print()

    print("=" * 65)
    print(f"[SUMMARY] Total Discovered Families: {len(families)} | Benchmark Status: SUCCESS")
    print("=" * 65)


if __name__ == "__main__":
    run_clustering_benchmark()
