# NextGen Smart Machine Studio

**A deterministic engineering configurator for special-purpose machinery.**  
Developed by **Aalap Janve** as a Master's Thesis portfolio project.

---

## What It Does

The NextGen Smart Machine Studio translates customer requirements into a complete, manufacturable machine concept in seconds. Unlike black-box AI solutions, every decision is deterministic, traceable, and explainable — exactly what an engineering team needs to review, sign off, and build.

1. **Input Requirements** — product type, throughput, quality constraints, budget, floor space
2. **Engine Synthesis** — deterministic rules, KPI computation, 3-stage module selection pipeline
3. **Output Concept** — process chain, module selections, line architecture, cost summary, full decision trace

---

## Core Philosophy: No AI, Full Explainability

The engine is built on first-principles engineering logic:

- **Transfer Functions** — mathematical relationships (nominal rate, takt time, parallel units, annual capacity)
- **Ordered Domain Rules** — cleanroom enforcement, inspection requirements, traceability, packaging
- **Canonical Operation Ordering** — feeding → assembly → insertion → testing → inspection → marking → packaging, with automatic resequencing when rules inject new steps
- **3-Stage Selection Pipeline** — Hard Filter → Capacity Model → Scoring
- **Architecture Selection** — Rotary / Pallet Conveyor / Linear Transport / Hybrid Flexible, based on nominal throughput and variant complexity

Every rule hit, filter stage, and module selection is logged in the **Decision Trace** — an engineering audit trail that can be exported alongside the concept report.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Deterministic Engine** | Same inputs always produce the same output. Reproducible by design. |
| **Knowledge Model** | Central engineering knowledge base with product taxonomy, operation ontology, transfer functions, and architecture rules. |
| **3-Stage Pipeline** | Stage 1: hard filter (industry, cleanroom, tolerance, variants). Stage 2: capacity model (parallel units). Stage 3: scoring (optimization priority). |
| **Feasibility Validation** | Real-time checks against budget and footprint limits with specific warnings. |
| **Bottleneck Detection** | Identifies stations whose cycle time exceeds the takt time buffer. |
| **Line Balancing** | Capacity utilization analysis with ideal range recommendations (30–85%). |
| **Full i18n** | Complete English and German interface support. |
| **Component Library** | Browse all validated modules, and add new ones with full field validation. |
| **Export** | JSON (for CAD/ERP integration) and Markdown (for engineering review). |
| **Flat Minimalist UI** | Clean, distraction-free interface with color-coded KPI cards and normalized progress bars. |

---

## Architecture

```
smart_machine_studio/
├── data/
│   ├── modules.json              # 25+ validated engineering modules
│   ├── products.json             # Product templates with base operations
│   └── schemas/                  # JSON Schema validation files
├── engine/
│   ├── concept.py                # Report generation orchestrator
│   ├── knowledge_model.py        # Central engineering knowledge base
│   ├── kpi.py                    # Deterministic KPI computation
│   ├── process_chain.py          # Process chain + architecture selection
│   ├── rules.py                  # Ordered domain rule engine
│   └── selection.py              # 3-stage module selection pipeline
├── ui/
│   └── app.py                    # Streamlit web interface
├── utils/
│   ├── i18n.py                   # Full EN/DE internationalization
│   └── validator.py              # JSON Schema + requirement validation
└── main.py                       # CLI entry point
```

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web UI
streamlit run ui/app.py
```

---

## Verification

The engine logic is covered by a comprehensive test suite that validates:

- Standard consumer product scenarios (60 ppm)
- Medical products with traceability requirements (laser marking + data logging)
- High-variant products triggering hybrid architecture
- High-throughput products triggering linear transport
- Budget overrun detection
- Architecture selection at different OEE/reject combinations
- Reproducibility (same inputs → same outputs)
- Bottleneck detection
- Low / high utilization recommendations
- Number formatting (compact k/M suffixes)
- Language toggle persistence

---

## Tech Stack

- **Python 3.12**
- **Streamlit** — web UI
- **jsonschema** — data validation (with graceful fallback)
- **No external AI/ML libraries** — the engine is purely deterministic rule-based logic

---

## About

This project was developed by **Aalap Janve** as a Master's Thesis portfolio project. The goal is to demonstrate how deterministic engineering synthesis can replace manual conceptual design for special-purpose machinery, with full traceability and no black-box decision-making.

---
