# 🛡️ Agent 10: Quality Audit & HITL Router

> **Agent Number:** 10 of 10  
> **Module Path:** [`backend/app/agents/agent_9_quality_audit.py`](file:///c:/Users/yx084/OneDrive/UniHack/backend/app/agents/agent_9_quality_audit.py)  
> **Role:** 12-Rule Integrity Auditor, 5-Pillar Confidence Calibrator & Human-In-The-Loop Router  
> **Key Technologies:** Deterministic Integrity Audit, Mathematical Confidence Decomposition, Variable-Level Caching, DBOM Provenance

---

## 🎯 Primary Mission

Agent 10 serves as the final quality gate before data delivery. It performs:
1. **12 Automated Contract Boundary Checks**: Validates character limits, registered marks (`®`, `™`), Master UOM single spacing (`24 in`), and 100% triple pairing.
2. **5-Pillar Evidence-Aware Confidence Scoring**:
   $$\text{Confidence} = 0.20 \cdot Q_{\text{retrieval}} + 0.20 \cdot A_{\text{authority}} + 0.20 \cdot C_{\text{consistency}} + 0.20 \cdot S_{\text{agreement}} + 0.20 \cdot V_{\text{validation}} - \text{Pen}_{\text{contradictions}} - \text{Pen}_{\text{missing}}$$
3. **Variable-Level Caching & HITL Routing**: If confidence $\ge 85\%$ or cached in Master KB / Human Overrides $\rightarrow$ Auto-approve. Otherwise $\rightarrow$ Route to HITL review queue.
4. **252-Column Final Delivery Assembly**: Assembles the complete 252-column canonical Unilog export record.
