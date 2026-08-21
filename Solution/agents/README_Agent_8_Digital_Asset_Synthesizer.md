# 🖼️ Agent 8: Digital Asset Synthesizer & Document Classifier Agent
### *OmniSpec AI — Canonical Asset Naming & Technical Document Governance Engine*

---

## 1. Architectural Blueprint & Component Topology

```mermaid
flowchart TD
    subgraph ASSET_INPUT ["📥 Product Identity & Document URLs"]
        A2_BRAND["Canonical Brand (e.g. 'Bosch®')"]
        A1_MPN["Clean MPN (e.g. 'SHX78B75UC')"]
        A5_PDF["Discovered OEM PDF URLs (from Agent 5)"]
    end

    subgraph AGENT_8_CORE ["⚙️ Agent 8 Asset Synthesizer Engine (DigitalAssetAgent)"]
        direction TB
        STEP1["1. Clean Brand Sanitizer<br/>• Strips ®, ™ and non-alphanumeric chars → 'BOSCH'"]
        STEP2["2. Primary & Alternate Image Formatter<br/>• Primary Image: <CleanBrand>_<MPN>.jpg ('BOSCH_SHX78B75UC.jpg')<br/>• Alternate Images 1..4: <CleanBrand>_<MPN>_1.jpg to _4.jpg"]
        STEP3["3. Technical Document Classifier & Submittal Builder<br/>• Spec Sheet: <CleanBrand>_<MPN>_Specification_Sheet.pdf<br/>• Maps Installation Manual, Owners Manual, SDS, RoHS<br/>• Autonomous 1-page engineering PDF generator (ReportLab)"]
        STEP4["4. Compliance & Verification Flags<br/>• Actual Image (Yes/No) = 'Yes'<br/>• Discontinued = 'No'<br/>• Country Of Origin normalization"]
        
        STEP1 --> STEP2 --> STEP3 --> STEP4
    end

    subgraph ASSET_OUTPUT ["📦 State Delta Output (ProductEnrichmentState)"]
        ASSETS["digital_assets: {'Product Image': 'BOSCH_SHX78B75UC.jpg', 'Specification Sheet': 'BOSCH_SHX78B75UC_Specification_Sheet.pdf', ...}"]
        FLAGS["compliance_flags: {'Actual Image (Yes/No)': 'Yes', 'Discontinued': 'No'}"]
    end

    ASSET_INPUT --> STEP1
    STEP4 --> ASSET_OUTPUT
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `BRAND_NAME` | Agent 2 | `Bosch®` |
| `MANUFACTURER_PART_NUMBER`| Agent 2 | `SHX78B75UC` |
| `raw_document_urls` | Agent 5 | List of discovered OEM PDF documents |

---

## 3. Digital Asset Naming Equations

$$\text{Primary Product Image} = \text{UPPERCASE}(\text{StripSymbols}(\text{Brand})) + \text{"\_"} + \text{MPN} + \text{".jpg"}$$
$$\text{Specification Sheet} = \text{UPPERCASE}(\text{StripSymbols}(\text{Brand})) + \text{"\_"} + \text{MPN} + \text{"\_Specification\_Sheet.pdf"}$$

### Canonical Asset Examples

| Brand | MPN | Primary Image Filename | Specification Sheet Filename |
| :--- | :--- | :--- | :--- |
| `Bosch®` | `SHX78B75UC` | `BOSCH_SHX78B75UC.jpg` | `BOSCH_SHX78B75UC_Specification_Sheet.pdf` |
| `Milwaukee®` | `49-94-0013` | `MILWAUKEE_49-94-0013.jpg` | `MILWAUKEE_49-94-0013_Specification_Sheet.pdf` |
| `SKF®` | `6205-2RS1` | `SKF_6205-2RS1.jpg` | `SKF_6205-2RS1_Specification_Sheet.pdf` |
| `Klein Tools®` | `11055` | `KLEIN_TOOLS_11055.jpg` | `KLEIN_TOOLS_11055_Specification_Sheet.pdf` |

---

## 4. Execution Telemetry & Performance
- **Average Latency:** $0.03\text{--}0.10\text{ ms}$ per SKU.
- **Trace Output:** Logs `[Agent 8 ✓] Digital Assets Generated: '<image_name>' (<ms> ms)`.
