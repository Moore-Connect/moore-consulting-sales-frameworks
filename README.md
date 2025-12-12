---
repository: moore-consulting-sales-frameworks
owner: Moore Consulting LLC
type: sales_strategy_frameworks
version: 1.0
license: MIT
---

# Moore Consulting Sales Frameworks

This repository contains the **sales strategy frameworks and reference implementations** used by Moore Consulting LLC to analyze pipeline health, deal momentum, execution readiness, and forecast integrity for fintech and data providers selling into institutional markets.

The intent of this repository is to make Moore Consulting’s sales methodology:
- explicit
- inspectable
- repeatable

All example data is synthetic and included solely for validation and demonstration.

---

## What’s in This Repository

### Sales Strategy Frameworks

Moore Consulting frameworks are published in two formats:
- **Markdown** for human consumption
- **JSON** for programmatic and AI-based use

Included frameworks:

**Pipeline Momentum Framework**  
Evaluates deal-level momentum using five execution signals:
- Engagement Depth  
- Stakeholder Expansion  
- Internal Activity  
- Reciprocity  
- Organizational Energy  

Files:
- `frameworks/pipeline-momentum-framework.md`
- `json/pipeline-momentum-framework.json`

**Sales Execution Model**  
A structured model for evaluating execution readiness across complex deals and stages.

Files:
- `frameworks/moore-sales-execution-model.md`
- `json/moore-sales-execution-model.json`

---

## Reference Implementation: Pipeline Momentum Analysis

This repository includes a Python reference implementation that applies the Pipeline Momentum Framework to structured deal data.

**Input**
- `test_deals.csv`
- Synthetic, manually scored deal-level signals (1–5 scale)
- No client or proprietary data

**Runner**
- `run_pipeline_momentum.py`

The runner:
- loads the framework definition
- scores each deal deterministically
- assigns a momentum band
- identifies weakest execution signals

**Outputs**
Generated in the `/output` directory:
- `pipeline_momentum_results.csv`  
  Structured deal-level results
- `pipeline_momentum_report.md`  
  A concise, client-readable momentum summary

---

## How to Run

From the repository root:
Results will be written to the /output directory.

Tests

Behavioral tests are included to validate framework integrity and scoring consistency.

test_frameworks.py
Executable framework validation

test_frameworks_behavior.py
Behavioral assertions for scoring logic

Tests ensure:

valid framework structure

signal boundaries and constraints

deterministic behavior across runs

Repository Structure
frameworks/
  pipeline-momentum-framework.md
  moore-sales-execution-model.md

json/
  pipeline-momentum-framework.json
  moore-sales-execution-model.json

run_pipeline_momentum.py
test_deals.csv
test_frameworks.py
test_frameworks_behavior.py
README.md
LICENSE

```bash
python run_pipeline_momentum.py
Results will be written to the /output directory.

Tests

Behavioral tests are included to validate framework integrity and scoring consistency.

test_frameworks.py
Executable framework validation

test_frameworks_behavior.py
Behavioral assertions for scoring logic

Tests ensure:

valid framework structure

signal boundaries and constraints

deterministic behavior across runs
Repository Structure
frameworks/
  pipeline-momentum-framework.md
  moore-sales-execution-model.md

json/
  pipeline-momentum-framework.json
  moore-sales-execution-model.json

run_pipeline_momentum.py
test_deals.csv
test_frameworks.py
test_frameworks_behavior.py
README.md
LICENSE

