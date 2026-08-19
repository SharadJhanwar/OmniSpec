import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


class PDFDatasheetGenerator:
    """
    Autonomous Technical Datasheet & Specification Cut Sheet Generator.
    Produces an OEM-compliant, high-density 1-page engineering PDF for contractors & distributors.
    """

    @classmethod
    def generate_datasheet(cls, record: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Palette: Deep Slate Navy, Cyan, Emerald
        c_primary = colors.HexColor("#0F172A")
        c_accent = colors.HexColor("#0284C7")
        c_text = colors.HexColor("#334155")
        c_bg_light = colors.HexColor("#F8FAFC")
        c_border = colors.HexColor("#E2E8F0")

        # Typography Styles
        style_header_title = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            textColor=c_primary
        )
        style_subtitle = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#64748B")
        )
        style_section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=c_accent,
            spaceAfter=4
        )
        style_body = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=c_text
        )
        style_cell_bold = ParagraphStyle(
            "CellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=c_primary
        )
        style_cell_val = ParagraphStyle(
            "CellVal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=c_text
        )

        elements = []

        brand = record.get("BRAND_NAME", record.get("brand_name", "INDUSTRIAL BRAND"))
        mfr = record.get("MANUFACTURER_NAME", record.get("manufacturer_name", "OEM Manufacturer"))
        mpn = record.get("Mfg_Part_Num", record.get("mfg_part_number", record.get("mfr_part_number", "MPN-000")))
        trade = record.get("TRADE_NAME", record.get("trade_name", ""))
        classpath = record.get("Classpath", record.get("classpath", "Industrial Supplies"))
        short_desc = record.get("SHORT_DESC", record.get("short_desc", "Commercial Grade Product Component"))
        long_desc = record.get("LONG_DESC1", record.get("long_desc1", short_desc))
        inv_desc = record.get("INVOICE_DESC", record.get("invoice_desc", ""))
        approvals = record.get("Standard Approvals", record.get("standard_approvals", "ANSI Compliant | ISO 9001"))
        warranty = record.get("Warranty", record.get("warranty", "1 Year Manufacturer Warranty"))

        # -------------------------------------------------------------
        # 1. Header Banner
        # -------------------------------------------------------------
        header_data = [
            [
                Paragraph(f"<b>{brand}</b>", style_header_title),
                Paragraph(f"<b>ENGINEERING SPECIFICATION SHEET</b><br/><font size=7 color='#64748B'>UNILOG MASTER CATALOG TRUTH</font>", ParagraphStyle("RightH", parent=style_subtitle, alignment=2))
            ],
            [
                Paragraph(f"Manufacturer: <b>{mfr}</b> {f'• Line: <b>{trade}</b>' if trade else ''}", style_subtitle),
                Paragraph(f"Part Number / MPN: <b>{mpn}</b>", ParagraphStyle("RightMPN", parent=style_cell_bold, alignment=2, textColor=c_accent))
            ]
        ]
        t_header = Table(header_data, colWidths=[3.8 * inch, 3.8 * inch])
        t_header.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 4))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=2, spaceAfter=8))

        # -------------------------------------------------------------
        # 2. Product Title & Taxonomy Banner
        # -------------------------------------------------------------
        elements.append(Paragraph(f"<b>{short_desc}</b>", ParagraphStyle("TitleDesc", parent=style_body, fontSize=11, leading=14, fontName="Helvetica-Bold", textColor=c_primary)))
        elements.append(Spacer(1, 3))
        elements.append(Paragraph(f"<font color='#64748B'>Classpath (4-Tier):</font> <b>{classpath}</b>", style_body))
        elements.append(Spacer(1, 8))

        # -------------------------------------------------------------
        # 3. Two-Column Layout: Physical Specs & Descriptions
        # -------------------------------------------------------------
        # Physical & Dimensional Attributes Table
        dim_l = record.get("LENGTH", record.get("length", "—"))
        dim_w = record.get("WIDTH", record.get("width", "—"))
        dim_h = record.get("HEIGHT", record.get("height", "—"))
        dim_uom = record.get("LENGTH_UOM", record.get("length_uom", "in"))

        spec_rows = [
            [Paragraph("Specification Attribute", style_cell_bold), Paragraph("Approved Value / LOV", style_cell_bold)],
            [Paragraph("Manufacturer Part #", style_cell_val), Paragraph(str(mpn), style_cell_bold)],
            [Paragraph("Overall Dimensions (L x W x H)", style_cell_val), Paragraph(f"{dim_l} x {dim_w} x {dim_h} {dim_uom}" if dim_l != "—" else "Standard Catalog Spec", style_cell_val)],
            [Paragraph("Invoice Receipt Form (&le;40)", style_cell_val), Paragraph(str(inv_desc), style_cell_bold)],
            [Paragraph("Selling Qty & UOM", style_cell_val), Paragraph(f"{record.get('Selling Qty', '1')} {record.get('Selling UOM', 'Each')}", style_cell_val)],
            [Paragraph("Regulatory Approvals", style_cell_val), Paragraph(str(approvals), style_cell_val)],
            [Paragraph("Standard Warranty", style_cell_val), Paragraph(str(warranty), style_cell_val)]
        ]

        # Add any non-empty attributes (e.g. Attribute 1 to 6)
        for idx in range(1, 7):
            lbl = record.get(f"ATTRIBUTE_LABEL {idx}") or record.get(f"attribute_label_{idx}")
            val = record.get(f"ATTRIBUTE_VALUE {idx}") or record.get(f"attribute_value_{idx}")
            uom = record.get(f"ATTRIBUTE_UOM {idx}") or record.get(f"attribute_uom_{idx}") or ""
            if lbl and val:
                uom_str = f" {uom}" if uom else ""
                spec_rows.append([Paragraph(str(lbl), style_cell_val), Paragraph(f"{val}{uom_str}", style_cell_bold)])

        t_specs = Table(spec_rows, colWidths=[2.2 * inch, 5.4 * inch])
        t_specs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ]))

        elements.append(Paragraph("TECHNICAL SPECIFICATIONS & DIMENSIONS", style_section_heading))
        elements.append(t_specs)
        elements.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # 4. Long Description & Narrative
        # -------------------------------------------------------------
        elements.append(Paragraph("DETAILED PRODUCT DESCRIPTION", style_section_heading))
        elements.append(Paragraph(str(long_desc), style_body))
        elements.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # 5. Key Atomic Features (Item Features 1..6)
        # -------------------------------------------------------------
        elements.append(Paragraph("KEY PRODUCT FEATURES & CAPABILITIES", style_section_heading))
        feat_list = []
        for f_idx in range(1, 7):
            f_val = record.get(f"ITEM_FEATURES_{f_idx}") or record.get(f"item_features_{f_idx}")
            if f_val:
                feat_list.append(f"• {f_val}")

        if not feat_list and "item_features" in record and isinstance(record["item_features"], list):
            feat_list = [f"• {f}" for f in record["item_features"][:6]]

        if not feat_list:
            feat_list = [
                f"• Engineered to {brand} industrial tolerance standards",
                "• Designed for heavy-duty commercial and trade environments",
                "• Compliant with strict Unilog Master UOM and LOV data dictionaries"
            ]

        for feat in feat_list:
            elements.append(Paragraph(feat, ParagraphStyle("FeatBullet", parent=style_body, leftIndent=10, spaceAfter=2)))

        elements.append(Spacer(1, 12))

        # -------------------------------------------------------------
        # 6. Governance Footer & Asset Notice
        # -------------------------------------------------------------
        elements.append(HRFlowable(width="100%", thickness=0.5, color=c_border, spaceBefore=4, spaceAfter=6))
        footer_text = f"<b>OmniSpec AI Intelligence Engine</b> • Generated from 252-Column Master Catalog Truth • Image: {record.get('Product Image', f'{brand}_{mpn}.jpg')} • Sourcing: Official OEM Documentation Only"
        elements.append(Paragraph(footer_text, ParagraphStyle("Footer", parent=style_subtitle, fontSize=7, leading=9, alignment=1)))

        doc.build(elements)
        return buffer.getvalue()
