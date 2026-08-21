from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class DeliveryProductRecord(BaseModel):
    """
    252-Column Unilog Master Delivery Standard Schema
    Matches 1-to-1 with 'Unihack_ Expected Output - Delivery Format.csv'
    """
    # 1. Sourcing & URLs (6 columns)
    mfr_url: str = Field(default="", alias="MFR URL")
    ref_url_1: str = Field(default="", alias="Ref URL 1")
    ref_url_2: str = Field(default="", alias="Ref URL 2")
    ref_url_3: str = Field(default="", alias="Ref URL 3")
    ref_url_4: str = Field(default="", alias="Ref URL 4")
    ref_url_5: str = Field(default="", alias="Ref URL 5")

    # 2. Core Identifiers (11 columns)
    part_number: str = Field(default="", alias="PART_NUMBER")
    dept: str = Field(default="", alias="Dept")
    class_name: str = Field(default="", alias="Class")
    fine: str = Field(default="", alias="Fine")
    sku: str = Field(default="", alias="SKU - MY_PART_NUMBER")
    mfg_part_num: str = Field(default="", alias="Mfg_Part_Num")
    part_desc: str = Field(default="", alias="Part_Desc")
    e1_brand: str = Field(default="", alias="E1_Brand")
    unilog_brand: str = Field(default="", alias="Unilog_Brand")
    dib_brand: str = Field(default="", alias="DIB_Brand")
    part_manuf: str = Field(default="", alias="Part_Manuf")

    # 3. Standardized Identifiers & Brand Master (5 columns)
    manufacturer_name: str = Field(default="", alias="MANUFACTURER_NAME")
    brand_name: str = Field(default="", alias="BRAND_NAME")
    trade_name: str = Field(default="", alias="TRADE_NAME")
    manufacturer_part_number: str = Field(default="", alias="MANUFACTURER_PART_NUMBER")
    alternate_part_number: str = Field(default="", alias="ALTERNATE_PART_NUMBER")

    # 4. Taxonomy & Multi-Channel Copy (7 columns)
    classpath: str = Field(default="", alias="Classpath")
    mobile_desc: str = Field(default="", alias="MOBILE_DESC")
    invoice_desc: str = Field(default="", alias="INVOICE_DESC")
    short_desc: str = Field(default="", alias="SHORT_DESC")
    long_desc1: str = Field(default="", alias="LONG_DESC1")
    retail_desc: str = Field(default="", alias="RETAIL_DESC")
    marketing_description: str = Field(default="", alias="MARKETING_DESCRIPTION")

    # 5. Feature Bullets & Special Fields (26 columns)
    item_features_1: str = Field(default="", alias="ITEM_FEATURES_1")
    item_features_2: str = Field(default="", alias="ITEM_FEATURES_2")
    item_features_3: str = Field(default="", alias="ITEM_FEATURES_3")
    item_features_4: str = Field(default="", alias="ITEM_FEATURES_4")
    item_features_5: str = Field(default="", alias="ITEM_FEATURES_5")
    item_features_6: str = Field(default="", alias="ITEM_FEATURES_6")
    item_features_7: str = Field(default="", alias="ITEM_FEATURES_7")
    item_features_8: str = Field(default="", alias="ITEM_FEATURES_8")
    item_features_9: str = Field(default="", alias="ITEM_FEATURES_9")
    item_features_10: str = Field(default="", alias="ITEM_FEATURES_10")
    item_features_11: str = Field(default="", alias="ITEM_FEATURES_11")
    item_features_12: str = Field(default="", alias="ITEM_FEATURES_12")
    item_features_13: str = Field(default="", alias="ITEM_FEATURES_13")
    item_features_14: str = Field(default="", alias="ITEM_FEATURES_14")
    item_features_15: str = Field(default="", alias="ITEM_FEATURES_15")
    item_features_16: str = Field(default="", alias="ITEM_FEATURES_16")
    item_features_17: str = Field(default="", alias="ITEM_FEATURES_17")
    item_features_18: str = Field(default="", alias="ITEM_FEATURES_18")
    item_features_19: str = Field(default="", alias="ITEM_FEATURES_19")
    item_features_20: str = Field(default="", alias="ITEM_FEATURES_20")
    with_features: str = Field(default="", alias="With")
    standard_approvals: str = Field(default="", alias="Standard/Approvals")
    prop_65: str = Field(default="", alias="Prop 65")
    application: str = Field(default="", alias="Application")
    includes: str = Field(default="", alias="Includes")
    product_name: str = Field(default="", alias="Product Name")

    # 6. Structured EAV Attributes (50 Triples = 150 Columns)
    attributes: Dict[str, str] = Field(default_factory=dict)

    # 7. Commercial, Logistics & Dimensions (19 columns)
    upc: str = Field(default="", alias="UPC")
    ean: str = Field(default="", alias="EAN")
    gtin: str = Field(default="", alias="GTIN")
    unspsc: str = Field(default="", alias="UNSPSC")
    warranty: str = Field(default="", alias="Warranty")
    list_price: str = Field(default="", alias="List Price")
    selling_qty: str = Field(default="", alias="Selling Qty")
    selling_uom: str = Field(default="", alias="Selling UOM")
    standard_packaging_info: str = Field(default="", alias="Standard Packaging Information")
    length: str = Field(default="", alias="LENGTH")
    length_uom: str = Field(default="", alias="LENGTH_UOM")
    height: str = Field(default="", alias="HEIGHT")
    height_uom: str = Field(default="", alias="HEIGHT_UOM")
    width: str = Field(default="", alias="WIDTH")
    width_uom: str = Field(default="", alias="WIDTH_UOM")
    weight: str = Field(default="", alias="WEIGHT")
    weight_uom: str = Field(default="", alias="WEIGHT_UOM")
    volume: str = Field(default="", alias="VOLUME")
    volume_uom: str = Field(default="", alias="VOLUME_UOM")

    # 8. Digital Assets, Docs & Metadata (28 columns)
    product_image: str = Field(default="", alias="Product Image")
    alternate_image_1: str = Field(default="", alias="Alternate Image 1")
    alternate_image_2: str = Field(default="", alias="Alternate Image 2")
    alternate_image_3: str = Field(default="", alias="Alternate Image 3")
    alternate_image_4: str = Field(default="", alias="Alternate Image 4")
    sds: str = Field(default="", alias="SDS")
    sds_1: str = Field(default="", alias="SDS_1")
    warranty_info: str = Field(default="", alias="Warranty Information")
    catalog: str = Field(default="", alias="Catalog")
    specification_sheet: str = Field(default="", alias="Specification Sheet")
    instruction_manual: str = Field(default="", alias="Instruction/Installation Manual")
    service_manual: str = Field(default="", alias="Service Manual")
    owners_manual: str = Field(default="", alias="Owners/User Manual")
    line_drawing: str = Field(default="", alias="Line Drawing")
    mtr: str = Field(default="", alias="MTR")
    rohs: str = Field(default="", alias="RoHS")
    full_engineering_drawing: str = Field(default="", alias="Full Engineering Drawing")
    energy_star_guide: str = Field(default="", alias="Energy Star Guide")
    technical_bulletin: str = Field(default="", alias="Technical Bulletin")
    submittal: str = Field(default="", alias="Submittal")
    compatibility_chart: str = Field(default="", alias="Compatibility Chart")
    size_chart: str = Field(default="", alias="Size Chart")
    product_label_insert: str = Field(default="", alias="Product Label/Insert")
    video_link: str = Field(default="", alias="Video Link")
    video_link_1: str = Field(default="", alias="Video Link 1")
    country_of_origin: str = Field(default="", alias="Country Of Origin")
    discontinued: str = Field(default="", alias="Discontinued")
    actual_image: str = Field(default="", alias="Actual Image (Yes/No)")

    model_config = ConfigDict(populate_by_name=True)

    def to_delivery_dict(self) -> Dict[str, str]:
        """Flatten into exact 252-column dictionary matching Unilog delivery headers."""
        result = {}
        # Core & Sourcing
        result["MFR URL"] = self.mfr_url
        result["Ref URL 1"] = self.ref_url_1
        result["Ref URL 2"] = self.ref_url_2
        result["Ref URL 3"] = self.ref_url_3
        result["Ref URL 4"] = self.ref_url_4
        result["Ref URL 5"] = self.ref_url_5
        result["PART_NUMBER"] = self.part_number
        result["Dept"] = self.dept
        result["Class"] = self.class_name
        result["Fine"] = self.fine
        result["SKU - MY_PART_NUMBER"] = self.sku
        result["Mfg_Part_Num"] = self.mfg_part_num
        result["Part_Desc"] = self.part_desc
        result["E1_Brand"] = self.e1_brand
        result["Unilog_Brand"] = self.unilog_brand
        result["DIB_Brand"] = self.dib_brand
        result["Part_Manuf"] = self.part_manuf
        result["MANUFACTURER_NAME"] = self.manufacturer_name
        result["BRAND_NAME"] = self.brand_name
        result["TRADE_NAME"] = self.trade_name
        result["MANUFACTURER_PART_NUMBER"] = self.manufacturer_part_number
        result["ALTERNATE_PART_NUMBER"] = self.alternate_part_number
        result["Classpath"] = self.classpath
        result["MOBILE_DESC"] = self.mobile_desc
        result["INVOICE_DESC"] = self.invoice_desc
        result["SHORT_DESC"] = self.short_desc
        result["LONG_DESC1"] = self.long_desc1
        result["RETAIL_DESC"] = self.retail_desc
        result["MARKETING_DESCRIPTION"] = self.marketing_description

        # Features 1..20
        for i in range(1, 21):
            attr_name = f"item_features_{i}"
            result[f"ITEM_FEATURES_{i}"] = getattr(self, attr_name, "")

        result["With"] = self.with_features
        result["Standard/Approvals"] = self.standard_approvals
        result["Prop 65"] = self.prop_65
        result["Application"] = self.application
        result["Includes"] = self.includes
        result["Product Name"] = self.product_name

        # Dynamic Attributes 1..50 (150 columns)
        for i in range(1, 51):
            result[f"ATTRIBUTE_LABEL {i}"] = self.attributes.get(f"ATTRIBUTE_LABEL {i}", "")
            result[f"ATTRIBUTE_VALUE {i}"] = self.attributes.get(f"ATTRIBUTE_VALUE {i}", "")
            result[f"ATTRIBUTE_UOM {i}"] = self.attributes.get(f"ATTRIBUTE_UOM {i}", "")

        # Commercial & Logistics
        result["UPC"] = self.upc
        result["EAN"] = self.ean
        result["GTIN"] = self.gtin
        result["UNSPSC"] = self.unspsc
        result["Warranty"] = self.warranty
        result["List Price"] = self.list_price
        result["Selling Qty"] = self.selling_qty
        result["Selling UOM"] = self.selling_uom
        result["Standard Packaging Information"] = self.standard_packaging_info
        result["LENGTH"] = self.length
        result["LENGTH_UOM"] = self.length_uom
        result["HEIGHT"] = self.height
        result["HEIGHT_UOM"] = self.height_uom
        result["WIDTH"] = self.width
        result["WIDTH_UOM"] = self.width_uom
        result["WEIGHT"] = self.weight
        result["WEIGHT_UOM"] = self.weight_uom
        result["VOLUME"] = self.volume
        result["VOLUME_UOM"] = self.volume_uom

        # Digital Assets
        result["Product Image"] = self.product_image
        result["Alternate Image 1"] = self.alternate_image_1
        result["Alternate Image 2"] = self.alternate_image_2
        result["Alternate Image 3"] = self.alternate_image_3
        result["Alternate Image 4"] = self.alternate_image_4
        result["SDS"] = self.sds
        result["SDS_1"] = self.sds_1
        result["Warranty Information"] = self.warranty_info
        result["Catalog"] = self.catalog
        result["Specification Sheet"] = self.specification_sheet
        result["Instruction/Installation Manual"] = self.instruction_manual
        result["Service Manual"] = self.service_manual
        result["Owners/User Manual"] = self.owners_manual
        result["Line Drawing"] = self.line_drawing
        result["MTR"] = self.mtr
        result["RoHS"] = self.rohs
        result["Full Engineering Drawing"] = self.full_engineering_drawing
        result["Energy Star Guide"] = self.energy_star_guide
        result["Technical Bulletin"] = self.technical_bulletin
        result["Submittal"] = self.submittal
        result["Compatibility Chart"] = self.compatibility_chart
        result["Size Chart"] = self.size_chart
        result["Product Label/Insert"] = self.product_label_insert
        result["Video Link"] = self.video_link
        result["Video Link 1"] = self.video_link_1
        result["Country Of Origin"] = self.country_of_origin
        result["Discontinued"] = self.discontinued
        result["Actual Image (Yes/No)"] = self.actual_image

        return result


UNILOG_DELIVERY_HEADERS = [
    "MFR URL", "Ref URL 1", "Ref URL 2", "Ref URL 3", "Ref URL 4", "Ref URL 5",
    "PART_NUMBER", "Dept", "Class", "Fine", "SKU - MY_PART_NUMBER", "Mfg_Part_Num", "Part_Desc",
    "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf", "MANUFACTURER_NAME", "BRAND_NAME",
    "TRADE_NAME", "MANUFACTURER_PART_NUMBER", "ALTERNATE_PART_NUMBER", "Classpath",
    "MOBILE_DESC", "INVOICE_DESC", "SHORT_DESC", "LONG_DESC1", "RETAIL_DESC", "MARKETING_DESCRIPTION",
    *[f"ITEM_FEATURES_{i}" for i in range(1, 21)],
    "With", "Standard/Approvals", "Prop 65", "Application", "Includes", "Product Name",
    *[col for i in range(1, 51) for col in (f"ATTRIBUTE_LABEL {i}", f"ATTRIBUTE_VALUE {i}", f"ATTRIBUTE_UOM {i}")],
    "UPC", "EAN", "GTIN", "UNSPSC", "Warranty", "List Price", "Selling Qty", "Selling UOM", "Standard Packaging Information",
    "LENGTH", "LENGTH_UOM", "HEIGHT", "HEIGHT_UOM", "WIDTH", "WIDTH_UOM", "WEIGHT", "WEIGHT_UOM", "VOLUME", "VOLUME_UOM",
    "Product Image", "Alternate Image 1", "Alternate Image 2", "Alternate Image 3", "Alternate Image 4",
    "SDS", "SDS_1", "Warranty Information", "Catalog", "Specification Sheet",
    "Instruction/Installation Manual", "Service Manual", "Owners/User Manual", "Line Drawing", "MTR", "RoHS",
    "Full Engineering Drawing", "Energy Star Guide", "Technical Bulletin", "Submittal", "Compatibility Chart",
    "Size Chart", "Product Label/Insert", "Video Link", "Video Link 1", "Country Of Origin", "Discontinued", "Actual Image (Yes/No)"
]
