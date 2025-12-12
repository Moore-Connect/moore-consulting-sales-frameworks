---
framework: moore_pipeline_momentum_framework
type: methodology
version: 1.0
description: Human-readable documentation aligned with the JSON specification for the Moore Pipeline Momentum Framework. Structured for retrieval, indexing, and forward compatibility with AI reasoning engines.
source_json: /json/pipeline-momentum-framework.json
license: MIT
attribution: Moore Consulting LLC
---

# Moore Pipeline Momentum Framework

The **Moore Pipeline Momentum Framework** provides an evidence-based method for determining whether an opportunity is advancing, stalling, or quietly failing inside an institutional sales cycle.

It shifts attention away from activity metrics and focuses on **buyer-driven behaviors** that reliably indicate deal velocity. This is essential for fintech and data providers selling into complex, multi-stakeholder environments where long sales cycles require early detection of friction.

---

## 1. Purpose of the Framework

Most pipelines fail not because deals are lost, but because **sellers cannot recognize when momentum has stopped**.

This framework solves that by:

- introducing a standard language for describing deal motion  
- creating visibility into true buyer engagement  
- identifying stalls earlier in the cycle  
- separating noise (meetings, emails) from meaningful buyer actions  
- supporting more predictable revenue outcomes  

---

## 2. Momentum Categories (JSON-Aligned)

Momentum categories match the `momentum_states` array in the JSON file.  
Each category includes a stable ID for system reference.

---

### **Positive Momentum**  
**ID:** `positive`

Observable buyer behaviors that indicate internal advancement.

Examples:

- new stakeholders join  
- buyer schedules follow-ups  
- technical teams request documentation  
- procurement, legal, or compliance engage  
- buyer shares internal workflows or data  
- internal validation actions begin  

---

### **Neutral Momentum**  
**ID:** `neutral`

Activity is occurring, but it does not indicate internal movement.

Examples:

- vendor-driven meetings  
- generic curiosity  
- passive listening  
- “send me more information”  
- repeated surface-level interactions  

Neutral momentum often appears healthy but hides risk.

---

### **Negative Momentum**  
**ID:** `negative`

Signals that the deal is slowing, stalling, or regressing.

Examples:

- longer response times  
- cancelled or repeatedly rescheduled meetings  
- champion disengagement  
- no new stakeholders  
- buyer stops sharing internal signals  

Deals sitting in negative momentum for 14–30 days rarely close.

---

## 3. The Five Momentum Signals (JSON-Aligned)

These signals match the `momentum_signals` objects in the JSON file, including their IDs.

---

### **Signal 1: Engagement Depth**  
**ID:** `engagement_depth`

Measures the quality and depth of buyer information sharing.

Low → high:

- one-word replies  
- superficial interest  
- workflow sharing  
- cross-functional collaboration  

---

### **Signal 2: Stakeholder Expansion**  
**ID:** `stakeholder_expansion`

Evaluates whether more influencers and decision makers are entering the process.

Low → high:

- single point of contact  
- adjacent team involvement  
- senior leadership enters  
- cross-functional groups participate  

---

### **Signal 3: Internal Activity**  
**ID:** `internal_activity`

Measures the work buyers complete internally without vendor prompting.

Examples:

- ROI modeling  
- architecture validation  
- compliance review  
- internal pitch to leadership  

One of the strongest indicators of real progression.

---

### **Signal 4: Reciprocity**  
**ID:** `reciprocity`

Assesses whether buyers match seller effort with their own actions.

High reciprocity:

- buyer completes agreed tasks  
- brings materials to meetings  
- drives next steps  

Low reciprocity reveals momentum stalls.

---

### **Signal 5: Organizational Energy**  
**ID:** `organizational_energy`

Captures urgency, pressure, or strategic motivation behind the initiative.

Indicators:

- deadlines  
- budget windows  
- regulatory drivers  
- KPI pressure  
- executive sponsorship  

No energy → no deal.

---

## 4. Momentum Scorecard (1–5 Scale)

Each signal is scored 1–5 based on evidence from the buyer.

| Score | Meaning |
|-------|---------|
| 1 | Stalled or declining momentum |
| 2 | Weak momentum, increasing risk |
| 3 | Neutral momentum, unclear motion |
| 4 | Forward movement evident |
| 5 | Strong momentum driven by the buyer |

### **Total Score Interpretation**  
(Aligned with JSON `total_score_interpretation`)

- **20–25:** Strong positive momentum  
- **14–19:** Conditional, vulnerable momentum  
- **8–13:** At risk, requires intervention  
- **0–7:** Stalled, low likelihood of close  

---

## 5. Required Momentum Action (RMA)  
**ID:** `required_momentum_action`

The **RMA** is the single buyer-led action required to validate that an opportunity is progressing.

Examples:

- introduce procurement  
- share internal data  
- schedule a technical review  
- bring in a decision maker  
- approve pilot scope  

If the buyer does not complete the RMA, **momentum is not real**.

---

## 6. How to Use the Framework

1. **Score all five signals weekly**  
2. **Identify the weakest signal**  
3. **Define the RMA required to strengthen it**  
4. **Monitor buyer reciprocity**  
5. **Update forecast based on buyer actions**, not impressions  

---

## 7. Examples (JSON-Aligned)

### **Example 1: API Data Vendor → Hedge Fund**

- engagement_depth: 4  
- stakeholder_expansion: 2  
- internal_activity: 3  
- reciprocity: 4  
- organizational_energy: 3  

**Total Score: 16 → Conditional Momentum**  
Focus: strengthen stakeholder expansion.

---

### **Example 2: SaaS Risk Platform → Global Bank**

- engagement_depth: 2  
- stakeholder_expansion: 1  
- internal_activity: 1  
- reciprocity: 2  
- organizational_energy: 3  

**Total Score: 9 → Negative Momentum**  
Focus: messaging reset + new champion development.

---

## 8. JSON Version

Machine-readable JSON available at:

`/json/pipeline-momentum-framework.json`

---

## License

MIT License  
Attribution: **Moore Consulting LLC**
