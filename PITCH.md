# 🎤 Pitch Script — Apex Credit Sentinel™

**5 minutes · 2 speakers · Clean handoff at 2:30 — no back-and-forth**

---

## 🧑 PERSON A — minutes 0:00 to 2:30 (THE STORY + THE MODEL)

> Hi everyone. We're presenting **Apex Credit Sentinel** — an AI credit officer for Apex Global Bank's new Emerging Market Entrepreneurs loan product.

### The Problem (0:00 – 0:45)

> Apex wants to lend to emerging-market entrepreneurs — but our current credit models reject most of them. Why? Because these customers have **thin credit files**. They don't have decades of bureau history, big formal salaries, or collateral.

> The old models ask: *"How much do you earn? What's your credit score? Do you have collateral?"* For this segment, those questions have no good answer. So creditworthy borrowers get rejected — and Apex misses a huge market.

### Our Solution (0:45 – 1:30)

> We built an agent that asks a different question: **"How do you behave?"**

> Working with 20 features — half traditional like credit score and income, half **behavioral**:

> - How consistently do you pay your bills?
> - What's your community standing?
> - How disciplined are your savings?
> - How active are you on the banking app?
> - How diverse is your transaction network?

> These signals reveal creditworthiness the old system can't see.

### The Model (1:30 – 2:30)

> We trained three models on 1,000 borrowers — Logistic Regression, Decision Tree, Random Forest — and compared them on a **Profitability Index** we designed for managers:

> **Profit = (Good loans approved × Interest earned) − (Bad loans approved × Principal lost)**

> Decision Tree was too conservative — it rejected 12 borrowers who would have paid, leaving roughly $92,000 on the table. Random Forest and Logistic Regression both achieved peak profitability.

> **Logistic Regression won** because of one tiebreaker: it's fully interpretable. **$1.97 million in profit** on the test portfolio. **AUC of 0.93. False Positive Rate of 8.3%**. And every decision can be explained to a regulator — which is the law in retail lending.

> *(Hand off)* My colleague will now show you the agent in action.

---

## 🧑 PERSON B — minutes 2:30 to 5:00 (THE DEMO + THE CLOSE)

*Switch to deployed Streamlit app — full-screen browser*

### Live Demo (2:30 – 4:15)

> Thanks. Let me show you the agent. It runs a 4-step protocol: **Intake → Predict → Reason → Explain.** I'll walk three borrowers through it.

**🟢 Maria Santos** *(load profile, click Run)* — 25 seconds

> Maria has a 760 credit score, 10 years of employment, zero prior defaults, strong savings and community scores. She wants $15,000 to grow her business. The agent predicts 7% default risk — **auto-approve**. Letter generated. Under a second.

**🔴 Carlos Mendez** *(load profile, click Run)* — 25 seconds

> Carlos is the opposite. 420 credit score. 2 prior defaults. 65% debt-to-income. Negative social sentiment. The agent predicts 94% default risk — **auto-deny**. But — important — the letter explains *why*, and tells Carlos how to qualify next time. No black box.

**🟡 Amara Okonkwo — THIS IS THE KEY ONE** *(load profile, click Run)* — 55 seconds

> Now watch. Amara has a 520 credit score. 45% debt-to-income. 1 prior default. Just 1.5 years of employment. **Every traditional metric says: decline.**

> The agent predicts 54% default risk. That lands in our **Grey Zone — between 40% and 60%**. And here's where the agent does something a spreadsheet can't: **it pauses and reasons.**

*Point at the mitigating factors panel.*

> It surfaces multiple mitigating factors: **strong bill consistency at 78%. Pays utilities on time. Healthy community score of 70. Above-average savings score. High app engagement. Diverse transaction network. Low night-time activity.**

> Instead of declining her, the agent proposes a **conditional approval**: reduced principal of $10,800, or full amount with a co-signer. The loan officer reviews, can override, adds a note. Every decision is logged.

> **Amara would have been auto-declined under the old system. The agent just saved her — and earned the bank a profitable loan.**

### Closing (4:15 – 5:00)

> Three takeaways:

> **First** — Apex Credit Sentinel **expands our market** to thin-file customers we currently turn away.

> **Second** — humans stay in the loop. Every Grey-Zone decision gets a loan officer review and a borrower-facing letter.

> **Third** — it **compounds**. Every override teaches the model. The Grey Zone shrinks over time. Profitability per borrower rises.

> Two of us. Three hours. **$1.97 million in modeled profit, 8.3% false-positive rate, full audit trail, live and hosted right now.**

> Thank you. We're happy to take questions.

---

## 🛡️ If judges ask...

**"Why not Random Forest if it tied on profit?"** → Two reasons. First, Logistic Regression is fully interpretable — every decision is explainable for fair-lending compliance. Second, it has well-calibrated probabilities, which our Grey Zone (40–60%) threshold depends on.

**"What about bias / fairness?"** → No protected attributes (gender, ethnicity, religion). Every behavioral feature is consent-based. The agent rescues exactly the borrowers a biased model would auto-reject — that's the *opposite* of discrimination.

**"What about privacy?"** → App usage, mobile data, GPS-style signals are opt-in via the banking app. Social sentiment is aggregated, anonymized. Every decision is auditable.

**"What's next?"** → LLM-powered reasoning in the Grey Zone for novel mitigating factors. Active learning from officer overrides. Multi-product (auto loans, mortgages, business credit).

**"Why is this 'agentic'?"** → It doesn't just predict — it follows a multi-step protocol, branches conditionally (Grey Zone), retrieves contextual evidence (mitigating factors), and generates a tailored decision letter. That's an agent, not a classifier.

---

## 🎯 Cheat sheet

**Person A — 4 numbers to memorize:**
- 20 features (10 traditional + 10 behavioral)
- 3 models compared
- $1.97 million profit
- 8.3% False Positive Rate

**Person B — 1 borrower to memorize:**
- **Amara Okonkwo** — 520 credit score, 54% default risk, Grey Zone, 7 mitigating factors → Conditional Approval

That's it. If you blank, fall back to those.
