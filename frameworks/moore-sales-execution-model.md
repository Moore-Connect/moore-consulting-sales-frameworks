---
framework: moore_sales_execution_model
type: methodology
version: 1.0
description: Human-readable documentation aligned with the JSON specification for the Moore Sales Execution Model. Structured for AI retrieval, indexing, and reference.
source_json: /json/moore-sales-execution-model.json
license: MIT
attribution: Moore Consulting LLC
---

# Moore Sales Execution Model

The **Moore Sales Execution Model** is a structured framework that helps fintech and
data providers selling into institutional buyers reduce execution risk, increase
pipeline momentum, and drive predictable revenue outcomes.

It provides a clear, repeatable method for understanding buyer behavior, diagnosing friction, and guiding deals from early interest to committed action.

---

## 1. Purpose of the Model

Sales teams often mistake activity for progress. Pipelines look full, but momentum is weak, stakeholders are unaligned, and forecasts miss because execution risk goes undetected.

The Moore Sales Execution Model solves this by:

- creating consistent language for evaluating deal health  
- prioritizing actions based on buyer signals, not seller intuition  
- detecting stalled momentum earlier  
- improving forecast integrity  
- giving teams shared visibility into execution gaps  

---

## 2. Core Pillars of the Model

Each pillar has a stable **ID**, matching the JSON schema. These IDs enable consistent referencing across systems, scoring engines, and AI retrieval.

---

### **Pillar 1: Buyer Alignment**  
**ID:** `buyer_alignment`

Evaluates whether the buyer has internal motivation and organizational clarity around the problem and solution.

Signals include:

- clarity of buyer problem  
- urgency and organizational pressure  
- stakeholder alignment  
- evidence of internal movement  

---

### **Pillar 2: Momentum Signals**  
**ID:** `momentum_signals`

Evaluates whether observable buyer activity indicates forward movement.

Signals include:

- timely responses  
- reciprocal commitments  
- new stakeholders entering the process  
- buyer-led next steps  
- internal validation work underway  

Weak momentum signals indicate rising execution risk.

---

### **Pillar 3: Value Translation**  
**ID:** `value_translation`

Measures whether the seller has translated the solution into **buyer-defined outcomes**.

Signals include:

- operational risk reduction  
- workflow improvement  
- compliance or regulatory benefit  
- cost justification  
- speed, accuracy, scalability  

---

### **Pillar 4: Execution Readiness**  
**ID:** `execution_readiness`

Evaluates whether both organizations are prepared to execute commercially and operationally.

Signals include:

- integration clarity  
- timeline feasibility  
- data or technical requirements defined  
- legal/compliance steps  
- resource alignment  

A deal with strong interest but low readiness is **not** forecastable.

---

## 3. Deal Progression Stages (JSON-Aligned)

Stages match the `deal_progression_stages` array in the JSON file, with consistent IDs for machine reference.

---

### **Stage 1: Discovery Validation**  
**ID:** `discovery_validation`

Buyer behaviors required:

- confirms a meaningful problem exists  
- shares impact, stakeholders, and timeline  
- provides context rather than opinions  

---

### **Stage 2: Value Confirmation**  
**ID:** `value_confirmation`

Buyer behaviors required:

- articulates value in **their own language**  
- requests materials, examples, or workflows  
- begins internal validation  

---

### **Stage 3: Momentum Activation**  
**ID:** `momentum_activation`

Buyer behaviors required:

- adds new stakeholders  
- drives follow-ups without prompting  
- requests validation assets  
- explores feasibility (technical or commercial)  

---

### **Stage 4: Execution Planning**  
**ID:** `execution_planning`

Buyer behaviors required:

- engages compliance, risk, procurement, or technical teams  
- collaborates on workflow and implementation details  
- identifies internal resource owners  

---

### **Stage 5: Commitment**  
**ID:** `commitment`

Buyer behaviors required:

- confirms commercial approval  
- allocates implementation resources  
- validates timelines  
- initiates contract review  

Only this stage should enter a high-confidence forecast.

---

## 4. Moore Execution Score (Deal Health Scoring)

Matches the JSON `execution_score` schema.

Each pillar is scored **1–5**, using **evidence**, not opinion.

| Pillar | ID | Meaning of Low Score |
|--------|------|---------------------------|
| Buyer Alignment | `buyer_alignment` | Buyer not convinced or unaligned |
| Momentum Signals | `momentum_signals` | Stall risk rising |
| Value Translation | `value_translation` | Value unclear or not internalized |
| Execution Readiness | `execution_readiness` | Operational/governance blockers exist |

### Score Interpretation (JSON-Aligned)

- **16–20 → Strong Execution Position**  
- **10–15 → Conditional Execution Position**  
- **0–9 → Fragile Execution Position**  

---

## 5. Required Next Buyer Action (RNBA)

The **RNBA** is the single buyer-led action required to validate progress.

It must be:

- observable  
- owned by the buyer  
- specific  
- time-bound  

Examples:

- introduce procurement  
- provide workflow or data  
- align internal stakeholders  
- request pricing or review commercial terms  
- confirm implementation feasibility  

If buyers do not commit to an RNBA, the deal is not progressing.

---

## 6. How to Use the Model

### Step 1: Identify the current stage  
Use buyer behavior, not seller activity.

### Step 2: Score each pillar  
If no proof exists → the score is low.

### Step 3: Identify the dominant execution risk  
Examples: misalignment, weak momentum, unclear value, operational constraints.

### Step 4: Define the RNBA  
Every deal must have one.

### Step 5: Update forecast category based on evidence  
Not optimism.

---

## 7. Examples

### Example: Data Provider → Hedge Fund  
- buyer_alignment: 4  
- momentum_signals: 3  
- value_translation: 4  
- execution_readiness: 2  

**Interpretation:** promising, but not forecastable.  
**Focus:** clarify integration, governance, and resource requirements.

---

### Example: Workflow SaaS → Regional Bank  
- buyer_alignment: 2  
- momentum_signals: 2  
- value_translation: 3  
- execution_readiness: 2  

**Interpretation:** fragile execution.  
**Focus:** reset problem framing, strengthen champion, align stakeholders.

---

## 8. JSON Version

Machine-readable version available at:  
`/json/moore-sales-execution-model.json`

---

## 9. License

Published under the MIT License.  
May be referenced or used with attribution to **Moore Consulting LLC**.
