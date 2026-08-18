# 🖼️ Agent 8: Digital Asset Synthesizer & Document Classifier Agent
### *OmniSpec AI — Canonical Asset Naming & Technical Document Governance Engine*

---

## 1. Agent Overview & Role

The **Digital Asset Synthesizer & Document Classifier Agent** standardizes product media, technical documentation, and compliance certificates into canonical Unilog naming conventions. B2B industrial distributors require uniform file naming architectures across CDNs and ERP digital asset management (DAM) repositories.

### Core Objectives:
1. **Canonical Media Naming:** Synthesize standardized primary and alternate image filenames following the rule:  
   $$\text{Primary Image} = \text{CleanBrand}\_\text{MPN}.\text{jpg}$$  
   $$\text{Alternate Image } k = \text{CleanBrand}\_\text{MPN}\_k.\text{jpg}$$
2. **Canonical Technical Document Naming:** Generate standardized PDF filenames for spec sheets:  
   $$\text{Spec Sheet} = \text{CleanBrand}\_\text{MPN}\_\text{Specification\_Sheet.pdf}$$
3. **Technical Document Classification:** Route and allocate official OEM PDF links to appropriate delivery columns (`Specification Sheet`, `Instruction/Installation Manual`, `Owners/User Manual`, `SDS`, `RoHS`, `Energy Star Guide`).
4. **Media Verification Flag:** Set `Actual Image (Yes/No)` based on verified asset existence and image resolution standards.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 8 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Brand, MPN & OEM Document URLs from Agents 2 & 5 ]                                             |
|   • Brand: "FRIGIDAIRE®", MPN: "PDSH4816AF"                                                        |
|   • Extracted OEM URLs: [Spec Sheet PDF, Installation PDF, Owners Manual PDF]                      |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Clean Brand Identifier: Strip ® / ™ and special characters ──► "FRIGIDAIRE"             │   |
|   │ 2. Synthesize Primary Image Name: "FRIGIDAIRE_PDSH4816AF.jpg"                              │   |
|   │ 3. Synthesize Alternate Images 1..4: "FRIGIDAIRE_PDSH4816AF_1.jpg" to "_4.jpg"             │   |
|   │ 4. Synthesize Spec Sheet PDF: "FRIGIDAIRE_PDSH4816AF_Specification_Sheet.pdf"              │   |
|   │ 5. Map OEM Manual & SDS URLs to Target Delivery Columns                                    │   |
|   │ 6. Set Compliance Flags: Actual Image = "Yes", Discontinued = "No"                         │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ▼                                                                                      |
|   [ 24 Digital Asset & Media Columns ] ───► Handed off to Agent 9 (Audit & HITL)                   |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `BRAND_NAME` | Agent 2 | `FRIGIDAIRE®` |
| `MANUFACTURER_PART_NUMBER`| Agent 2 | `PDSH4816AF` |
| `raw_document_urls` | Agent 5 | List of discovered OEM PDF documents |
| `image_urls` | Agent 5 | List of high-res image URLs from OEM page |

---

## 3. Digital Asset Naming Standards

As mandated by the Unilog Content Guidelines:
- Brand names in asset filenames must be **UPPERCASE** with all non-alphanumeric characters stripped.
- Delimiters between Brand, MPN, and index must strictly be underscores (`_`).

```python
import re

def synthesize_asset_names(brand_name: str, mpn: str) -> dict:
    clean_brand = re.sub(r"[^A-Za-z0-9]", "", brand_name).upper()
    clean_mpn = re.sub(r"[^A-Za-z0-9_-]", "", mpn)
    
    prefix = f"{clean_brand}_{clean_mpn}"
    
    return {
        "Product Image": f"{prefix}.jpg",
        "Alternate Image 1": f"{prefix}_1.jpg",
        "Alternate Image 2": f"{prefix}_2.jpg",
        "Alternate Image 3": f"{prefix}_3.jpg",
        "Alternate Image 4": f"{prefix}_4.jpg",
        "Specification Sheet": f"{prefix}_Specification_Sheet.pdf"
    }
```

---

## 4. Technical Document Mapping Grid

The agent populates up to 24 technical document and media columns:

| Column Name | Value Generated | Source Document Type |
| :--- | :--- | :--- |
| `Product Image` | `FRIGIDAIRE_PDSH4816AF.jpg` | Primary product photo |
| `Alternate Image 1` | `FRIGIDAIRE_PDSH4816AF_1.jpg` | Side / Interior view |
| `Alternate Image 2` | `FRIGIDAIRE_PDSH4816AF_2.jpg` | Top rack view |
| `Alternate Image 3` | `FRIGIDAIRE_PDSH4816AF_3.jpg` | Lower rack view |
| `Alternate Image 4` | `FRIGIDAIRE_PDSH4816AF_4.jpg` | Dimension diagram |
| `Specification Sheet` | `FRIGIDAIRE_PDSH4816AF_Specification_Sheet.pdf` | OEM Engineering Submittal |
| `Instruction/Installation Manual` | `https://www.whirlpool.com/.../installation-instructions.pdf` | Installation Guide |
| `Owners/User Manual` | `https://www.whirlpool.com/.../owners-manual.pdf` | User Guide |
| `SDS` | `https://multimedia.3m.com/.../sds.pdf` | Safety Data Sheet (Abrasives/Chemicals) |
| `Energy Star Guide` | `https://.../energystar-guide.pdf` | Energy Star Rating Certificate |
| `Country Of Origin` | `United States` | Derived from OEM documentation |
| `Discontinued` | `No` | Active product flag |
| `Actual Image (Yes/No)` | `Yes` | High-res image verification flag |

---

## 5. Output Schema & 252-Column Target Mapping

```json
{
  "Product Image": "FRIGIDAIRE_PDSH4816AF.jpg",
  "Alternate Image 1": "FRIGIDAIRE_PDSH4816AF_1.jpg",
  "Alternate Image 2": "FRIGIDAIRE_PDSH4816AF_2.jpg",
  "Alternate Image 3": "FRIGIDAIRE_PDSH4816AF_3.jpg",
  "Alternate Image 4": "FRIGIDAIRE_PDSH4816AF_4.jpg",
  "Specification Sheet": "FRIGIDAIRE_PDSH4816AF_Specification_Sheet.pdf",
  "Instruction/Installation Manual": "",
  "Owners/User Manual": "",
  "SDS": "",
  "RoHS": "",
  "Energy Star Guide": "",
  "Country Of Origin": "",
  "Discontinued": "",
  "Actual Image (Yes/No)": "Yes"
}
```

---

## 6. Worked Test Case

### Test Input:
```csv
BRAND_NAME: Whirlpool®
MANUFACTURER_PART_NUMBER: WDTS7024RZ
```

### Agent 8 Execution:
1. **Brand Clean:** `Whirlpool®` $\rightarrow$ `WHIRLPOOL`.
2. **Primary Image:** `Whirlpool_WDTS7024RZ.jpg`.
3. **Spec Sheet:** `Whirlpool_WDTS7024RZ_Specification_Sheet.pdf`.
4. **Manuals:** Maps Whirlpool installation PDF and owners manual PDF into corresponding columns.
5. **Flag:** `Actual Image (Yes/No)` = `Yes`.
