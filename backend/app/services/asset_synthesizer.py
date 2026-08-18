import re
from typing import Dict


class DigitalAssetSynthesizer:
    """
    Standardizes digital asset filenames and technical document naming
    according to Unilog Internal Content Guidelines (<Brand>_<MPN>.<ext>).
    """

    @classmethod
    def synthesize_media_filenames(cls, brand_name: str, mpn: str) -> Dict[str, str]:
        """
        Synthesizes standard image and PDF names:
        'FRIGIDAIRE®', 'PDSH4816AF' ->
        {
            'Product Image': 'FRIGIDAIRE_PDSH4816AF.jpg',
            'Alternate Image 1': 'FRIGIDAIRE_PDSH4816AF_1.jpg',
            'Alternate Image 2': 'FRIGIDAIRE_PDSH4816AF_2.jpg',
            'Alternate Image 3': 'FRIGIDAIRE_PDSH4816AF_3.jpg',
            'Alternate Image 4': 'FRIGIDAIRE_PDSH4816AF_4.jpg',
            'Specification Sheet': 'FRIGIDAIRE_PDSH4816AF_Specification_Sheet.pdf'
        }
        """
        if not brand_name:
            brand_name = "UNBRANDED"
        if not mpn:
            mpn = "ITEM"

        # Clean brand name: strip ®/™, special characters, convert to UPPERCASE
        clean_brand = re.sub(r"[^A-Za-z0-9]", "", brand_name).upper()
        # Clean MPN: keep alphanumeric, hyphens, underscores
        clean_mpn = re.sub(r"[^A-Za-z0-9_-]", "", mpn)

        prefix = f"{clean_brand}_{clean_mpn}"

        return {
            "Product Image": f"{prefix}.jpg",
            "Alternate Image 1": f"{prefix}_1.jpg",
            "Alternate Image 2": f"{prefix}_2.jpg",
            "Alternate Image 3": f"{prefix}_3.jpg",
            "Alternate Image 4": f"{prefix}_4.jpg",
            "Specification Sheet": f"{prefix}_Specification_Sheet.pdf",
            "Actual Image (Yes/No)": "Yes"
        }
