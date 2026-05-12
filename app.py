"""
APEX GLOBAL BANK — APEX CREDIT SENTINEL™
Agentic AI Credit Officer for Emerging Market Entrepreneurs

Protocol:
  1. INTAKE  — load borrower profile
  2. PREDICT — query winning ML model
  3. REASON  — if P(default) ∈ [40%, 60%] Grey Zone, search mitigating factors
  4. EXPLAIN — produce plain-language decision letter
"""

import os
import json
import joblib
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Apex Credit Sentinel™", page_icon="🏦",
                    layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0A2540 0%, #1E4D7B 100%);
        padding: 1.5rem 2rem; border-radius: 8px; color: white; margin-bottom: 2rem;
    }
    .main-header h1 { color: white !important; margin: 0; font-size: 2rem; }
    .main-header p { color: #B8D4E8; margin: 0.3rem 0 0 0; }
    .decision-approve { background: #E8F5E9; border-left: 6px solid #2E7D32;
                         padding: 1.2rem; border-radius: 6px; margin: 1rem 0; }
    .decision-deny { background: #FFEBEE; border-left: 6px solid #C62828;
                      padding: 1.2rem; border-radius: 6px; margin: 1rem 0; }
    .decision-grey { background: #FFF8E1; border-left: 6px solid #F57F17;
                      padding: 1.2rem; border-radius: 6px; margin: 1rem 0; }
    .protocol-box { background: #F8FAFC; border: 1px solid #E0E6ED;
                     padding: 1rem; border-radius: 6px;
                     font-family: 'Courier New', monospace; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

BASE = Path(__file__).parent

@st.cache_resource
def load_assets():
    model_path = BASE / 'best_model.joblib'
    meta_path = BASE / 'model_meta.json'
    need_train = not (model_path.exists() and meta_path.exists())
    if not need_train:
        try:
            joblib.load(model_path)
        except Exception:
            need_train = True
    if need_train:
        with st.spinner("First-time setup: training model (≈10s)..."):
            import subprocess, sys
            subprocess.run([sys.executable, str(BASE / '02_train_models.py')],
                           check=True, cwd=str(BASE))
    model = joblib.load(model_path)
    with open(meta_path) as f:
        meta = json.load(f)
    return model, meta

model, meta = load_assets()
THRESHOLD = meta.get('decision_threshold', 0.65)

st.markdown(f"""
<div class='main-header'>
  <h1>🏦 Apex Credit Sentinel™</h1>
  <p>Agentic AI Credit Officer · Emerging Market Entrepreneurs Loan Product</p>
  <p style='font-size:0.85rem;'>Model: <b>{meta['winning_model']}</b> ·
  AUC = {meta['metrics']['AUC_ROC']} ·
  Test FPR = {meta['metrics']['False_Positive_Rate']:.1%} ·
  Test Profit = ${meta['metrics']['Profitability_USD']:,.0f}</p>
</div>
""", unsafe_allow_html=True)

# Demo profiles — designed against the new schema
PROFILES = {
    "🟢 Maria S. (strong applicant)": dict(
        name="Maria Santos",
        Age=42, Monthly_Income=8500.0, Debt_to_Income=0.18, Credit_Score=760,
        Loan_Amount=15000.0, Employment_Years=10.0, Dependants=1, Prior_Defaults=0,
        Collateral_Value=45000.0, Credit_Accounts=8,
        Utility_Latency=0.4, App_Session_Time=95.0, Social_Sentiment=0.55,
        Mobile_Data_Use=25.0, Ecommerce_Freq=18, Savings_Score=85.0,
        Community_Score=82.0, Night_Activity=0.10, Contact_Diversity=270,
        Bill_Consistency=0.92,
    ),
    "🔴 Carlos M. (high-risk applicant)": dict(
        name="Carlos Mendez",
        Age=24, Monthly_Income=1800.0, Debt_to_Income=0.65, Credit_Score=420,
        Loan_Amount=35000.0, Employment_Years=0.5, Dependants=4, Prior_Defaults=2,
        Collateral_Value=8000.0, Credit_Accounts=3,
        Utility_Latency=28.0, App_Session_Time=12.0, Social_Sentiment=-0.40,
        Mobile_Data_Use=3.0, Ecommerce_Freq=1, Savings_Score=15.0,
        Community_Score=22.0, Night_Activity=0.70, Contact_Diversity=55,
        Bill_Consistency=0.12,
    ),
    "🟡 Amara O. (borderline — hidden strength)  ⭐ Pitch demo case": dict(
        name="Amara Okonkwo",
        # Weak on paper: low credit, high DTI, modest income, 1 prior default
        Age=29, Monthly_Income=2400.0, Debt_to_Income=0.45, Credit_Score=520,
        Loan_Amount=18000.0, Employment_Years=1.5, Dependants=2, Prior_Defaults=1,
        Collateral_Value=12000.0, Credit_Accounts=4,
        # But behavioral signals are strong: consistent bills, good community/savings
        Utility_Latency=0.8, App_Session_Time=85.0, Social_Sentiment=0.35,
        Mobile_Data_Use=18.0, Ecommerce_Freq=11, Savings_Score=68.0,
        Community_Score=70.0, Night_Activity=0.15, Contact_Diversity=210,
        Bill_Consistency=0.78,
    ),
}

st.sidebar.markdown("### 📋 STEP 1 — INTAKE")
preset_choice = st.sidebar.selectbox(
    "Quick-load a borrower profile:",
    options=["— Manual entry —"] + list(PROFILES.keys())
)
p = PROFILES.get(preset_choice, {})
name_default = p.get('name', "Test Applicant")

with st.sidebar.form("intake_form"):
    name = st.text_input("Applicant Name", value=name_default)

    st.markdown("**Traditional indicators**")
    Age = st.number_input("Age", 18, 75, value=int(p.get('Age', 35)))
    Monthly_Income = st.number_input("Monthly Income (USD)", 0.0, 30000.0,
                                       value=float(p.get('Monthly_Income', 3000)))
    Debt_to_Income = st.slider("Debt-to-Income ratio", 0.0, 1.0,
                                 value=float(p.get('Debt_to_Income', 0.30)), step=0.01)
    Credit_Score = st.number_input("Credit Score", 300, 850,
                                     value=int(p.get('Credit_Score', 640)))
    Loan_Amount = st.number_input("Loan Amount Requested (USD)", 1000.0, 100000.0,
                                    value=float(p.get('Loan_Amount', 15000)))
    Employment_Years = st.number_input("Employment (years)", 0.0, 50.0,
                                         value=float(p.get('Employment_Years', 5.0)), step=0.5)
    Dependants = st.number_input("Number of Dependants", 0, 10,
                                   value=int(p.get('Dependants', 1)))
    Prior_Defaults = st.number_input("Prior Defaults", 0, 10,
                                       value=int(p.get('Prior_Defaults', 0)))
    Collateral_Value = st.number_input("Collateral Value (USD)", 0.0, 500000.0,
                                         value=float(p.get('Collateral_Value', 20000)))
    Credit_Accounts = st.number_input("Credit Accounts", 0, 30,
                                        value=int(p.get('Credit_Accounts', 5)))

    st.markdown("**Behavioral indicators**")
    Utility_Latency = st.number_input("Utility Payment Latency (days)", 0.0, 60.0,
                                        value=float(p.get('Utility_Latency', 4.0)))
    App_Session_Time = st.number_input("App Session Time (min/month)", 0.0, 200.0,
                                         value=float(p.get('App_Session_Time', 50.0)))
    Social_Sentiment = st.slider("Social Sentiment (-1 to 1)", -1.0, 1.0,
                                   value=float(p.get('Social_Sentiment', 0.15)), step=0.01)
    Mobile_Data_Use = st.number_input("Mobile Data Use (GB/month)", 0.0, 100.0,
                                        value=float(p.get('Mobile_Data_Use', 13.0)))
    Ecommerce_Freq = st.number_input("E-commerce Purchases/month", 0, 50,
                                       value=int(p.get('Ecommerce_Freq', 10)))
    Savings_Score = st.slider("Savings Score (0-100)", 0.0, 100.0,
                                value=float(p.get('Savings_Score', 60.0)), step=1.0)
    Community_Score = st.slider("Community Score (0-100)", 0.0, 100.0,
                                  value=float(p.get('Community_Score', 65.0)), step=1.0)
    Night_Activity = st.slider("Night Activity (0-1)", 0.0, 1.0,
                                 value=float(p.get('Night_Activity', 0.27)), step=0.01)
    Contact_Diversity = st.number_input("Contact Diversity", 0, 500,
                                          value=int(p.get('Contact_Diversity', 215)))
    Bill_Consistency = st.slider("Bill Consistency (0-1)", 0.0, 1.0,
                                   value=float(p.get('Bill_Consistency', 0.63)), step=0.01)

    submitted = st.form_submit_button("🤖 Run Apex Sentinel Agent",
                                       use_container_width=True, type="primary")


def build_borrower_df(d: dict) -> pd.DataFrame:
    return pd.DataFrame([{k: d[k] for k in meta['features']}])

def detect_mitigating_factors(d: dict) -> list:
    factors = []
    if d['Bill_Consistency'] >= 0.75:
        factors.append(f"Strong bill-payment consistency ({d['Bill_Consistency']:.2f}) — disciplined payment habit")
    if d['Utility_Latency'] <= 1.5:
        factors.append("Pays utility bills on time or early")
    if d['Community_Score'] >= 65:
        factors.append(f"Healthy community score ({d['Community_Score']:.0f}/100)")
    if d['Savings_Score'] >= 60:
        factors.append(f"Above-average savings score ({d['Savings_Score']:.0f}/100)")
    if d['App_Session_Time'] >= 70:
        factors.append("High banking-app engagement — financially attentive")
    if d['Social_Sentiment'] >= 0.30:
        factors.append(f"Positive social sentiment (+{d['Social_Sentiment']:.2f})")
    if d['Contact_Diversity'] >= 200:
        factors.append("Diverse social/transaction network")
    if d['Night_Activity'] <= 0.20:
        factors.append("Low night-time spending — stable lifestyle pattern")
    if d['Collateral_Value'] >= d['Loan_Amount'] * 0.5:
        factors.append(f"Collateral covers ≥50% of requested loan (${d['Collateral_Value']:,.0f})")
    if d['Ecommerce_Freq'] >= 10:
        factors.append("Active e-commerce participant — diversified spending")
    return factors

def detect_aggravating_factors(d: dict) -> list:
    flags = []
    if d['Prior_Defaults'] >= 1:
        flags.append(f"{d['Prior_Defaults']} prior default(s) on record")
    if d['Credit_Score'] < 550:
        flags.append(f"Low credit score ({d['Credit_Score']})")
    if d['Debt_to_Income'] >= 0.50:
        flags.append(f"High debt-to-income ratio ({d['Debt_to_Income']:.0%})")
    if d['Utility_Latency'] >= 10:
        flags.append(f"Chronically late utility payments (~{d['Utility_Latency']:.0f} days)")
    if d['Bill_Consistency'] < 0.30:
        flags.append(f"Poor bill-payment consistency ({d['Bill_Consistency']:.2f})")
    if d['Employment_Years'] < 1.0:
        flags.append("Less than 1 year of employment history")
    if d['Social_Sentiment'] <= -0.20:
        flags.append(f"Negative social sentiment ({d['Social_Sentiment']:+.2f})")
    if d['Night_Activity'] >= 0.60:
        flags.append("High night-time activity — irregular spending pattern")
    return flags

def generate_letter(name, decision, prob_paid, mitigators, aggravators, loan_amount, note=""):
    today = datetime.now().strftime("%B %d, %Y")
    pd_pct = (1 - prob_paid) * 100

    if decision == "APPROVE":
        body = f"""We are pleased to inform you that your loan application with Apex Global Bank for USD {loan_amount:,.0f} has been **APPROVED**.

After a careful review, our risk team determined that you meet our criteria for the Emerging Market Entrepreneurs loan program. The factors that supported your approval include:

{chr(10).join('• ' + m for m in mitigators[:5]) if mitigators else '• A solid overall credit profile.'}

Our records indicate an estimated probability of default of {pd_pct:.1f}%, which is within our acceptable risk threshold.

A relationship manager will contact you within 2 business days to finalize the loan agreement."""
    elif decision == "DENY":
        body = f"""Thank you for applying to the Apex Global Bank Emerging Market Entrepreneurs loan program for USD {loan_amount:,.0f}.

After careful review, we are unable to approve your application at this time. Our decision is based on the following factors:

{chr(10).join('• ' + a for a in aggravators[:5]) if aggravators else '• Insufficient risk profile match for this product.'}

Our analysis estimates a probability of default of {pd_pct:.1f}%, which exceeds our risk threshold.

To improve future eligibility, we recommend:

• Reducing existing debts and avoiding overdrafts for 6+ consecutive months
• Establishing consistent on-time bill and utility payments
• Building a longer banking relationship history with Apex

You have the right to request a review of this decision within 30 days."""
    else:
        body = f"""Thank you for applying to the Apex Global Bank Emerging Market Entrepreneurs loan program for USD {loan_amount:,.0f}.

Your application has been escalated to our **Conditional Review** track. While certain traditional indicators in your profile fall below our standard thresholds, our behavioral analysis has identified meaningful mitigating factors:

{chr(10).join('• ' + m for m in mitigators[:5])}

We estimate a probability of default of {pd_pct:.1f}%, which falls within our Grey Zone (40–60%). Rather than declining your application outright, we are prepared to offer a **conditional approval** subject to one of the following options:

• A reduced principal of USD {loan_amount*0.6:,.0f} on the same term, **OR**
• The full requested amount with a co-signer or additional collateral

A relationship manager will contact you within 3 business days to discuss these options."""

    if note:
        body += f"\n\n**Loan Officer Note:** {note}"

    return f"""**APEX GLOBAL BANK**
*Risk Management Division*
{today}

Dear {name},

{body}

Sincerely,

**Risk Management Office**
Apex Global Bank

---
*This letter was prepared with the assistance of Apex Credit Sentinel™ and reviewed by a Loan Officer in accordance with our Human-in-the-Loop policy.*"""


# Main panel
col_left, col_right = st.columns([2, 1])

with col_right:
    st.markdown("### 🧭 Agent Protocol")
    st.markdown("""
<div class='protocol-box'>
1. <b>INTAKE</b> — read borrower profile<br>
2. <b>PREDICT</b> — query best model<br>
3. <b>REASON</b> — if 40% ≤ P(default) ≤ 60%, search mitigating factors<br>
4. <b>EXPLAIN</b> — generate decision letter
</div>
    """, unsafe_allow_html=True)
    st.markdown("### ⚖️ Decision Thresholds")
    st.markdown("""
- **P(default) < 40%** → AUTO-APPROVE
- **40% ≤ P(default) ≤ 60%** → GREY ZONE — invoke reasoning
- **P(default) > 60%** → AUTO-DENY
    """)
    st.markdown("### 🔬 Model in Production")
    st.metric("Model", meta['winning_model'])
    st.metric("AUC-ROC", f"{meta['metrics']['AUC_ROC']}")
    st.metric("False Positive Rate", f"{meta['metrics']['False_Positive_Rate']:.1%}")
    st.metric("Test-set Profit", f"${meta['metrics']['Profitability_USD']:,.0f}")

with col_left:
    if not submitted:
        st.info("👈 Select a sample profile or enter borrower details, then click **Run Apex Sentinel Agent**.")
        st.markdown("### 🎯 Why this product exists")
        st.markdown(
            "Emerging-market entrepreneurs are routinely declined by legacy "
            "credit models because they lack thick traditional credit files. "
            "Apex Credit Sentinel reads **behavioral signals** — bill consistency, "
            "savings habits, community engagement, app activity, network quality — "
            "to find creditworthy borrowers conventional models miss."
        )
        st.markdown("**Try the ⭐ Borderline Case** to see the agent rescue a borrower who looks bad on paper but has a hidden strength.")
    else:
        intake = dict(
            Age=Age, Monthly_Income=Monthly_Income, Debt_to_Income=Debt_to_Income,
            Credit_Score=Credit_Score, Loan_Amount=Loan_Amount,
            Employment_Years=Employment_Years, Dependants=Dependants,
            Prior_Defaults=Prior_Defaults, Collateral_Value=Collateral_Value,
            Credit_Accounts=Credit_Accounts,
            Utility_Latency=Utility_Latency, App_Session_Time=App_Session_Time,
            Social_Sentiment=Social_Sentiment, Mobile_Data_Use=Mobile_Data_Use,
            Ecommerce_Freq=Ecommerce_Freq, Savings_Score=Savings_Score,
            Community_Score=Community_Score, Night_Activity=Night_Activity,
            Contact_Diversity=Contact_Diversity, Bill_Consistency=Bill_Consistency,
        )

        with st.status("Running Apex Sentinel protocol...", expanded=True) as status:
            st.write("**STEP 1 — INTAKE**: borrower profile loaded ✓")
            X_borrower = build_borrower_df(intake)
            prob_paid = float(model.predict_proba(X_borrower)[0, 1])
            prob_default = 1 - prob_paid
            st.write(f"**STEP 2 — PREDICT**: P(default) = **{prob_default:.1%}**, "
                     f"P(paid) = {prob_paid:.1%} ✓")

            in_grey_zone = 0.40 <= prob_default <= 0.60
            mitigators = detect_mitigating_factors(intake)
            aggravators = detect_aggravating_factors(intake)

            if in_grey_zone:
                st.write(f"**STEP 3 — REASON**: 🟡 GREY ZONE entered. Searching for mitigating factors...")
                st.write(f"   → Found **{len(mitigators)}** mitigating factor(s) and **{len(aggravators)}** aggravating factor(s)")
                decision = "GREY"
            elif prob_default < 0.40:
                st.write(f"**STEP 3 — REASON**: 🟢 Low risk — auto-approve path")
                decision = "APPROVE"
            else:
                st.write(f"**STEP 3 — REASON**: 🔴 High risk — auto-deny path")
                decision = "DENY"

            st.write("**STEP 4 — EXPLAIN**: generating decision letter ✓")
            status.update(label="✅ Protocol complete", state="complete", expanded=False)

        if decision == "APPROVE":
            st.markdown(f"""
<div class='decision-approve'>
<h3 style='margin:0;'>🟢 RECOMMENDATION: APPROVE</h3>
<p style='margin:0.4rem 0 0 0;'>P(default) = {prob_default:.1%} · Loan: USD {Loan_Amount:,.0f}</p>
</div>""", unsafe_allow_html=True)
        elif decision == "DENY":
            st.markdown(f"""
<div class='decision-deny'>
<h3 style='margin:0;'>🔴 RECOMMENDATION: DENY</h3>
<p style='margin:0.4rem 0 0 0;'>P(default) = {prob_default:.1%} · Loan: USD {Loan_Amount:,.0f}</p>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class='decision-grey'>
<h3 style='margin:0;'>🟡 RECOMMENDATION: CONDITIONAL APPROVAL (Grey Zone)</h3>
<p style='margin:0.4rem 0 0 0;'>P(default) = {prob_default:.1%} · Loan: USD {Loan_Amount:,.0f} · {len(mitigators)} mitigating factor(s) found</p>
</div>""", unsafe_allow_html=True)

        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("#### ✅ Mitigating Factors")
            if mitigators:
                for m in mitigators:
                    st.markdown(f"- {m}")
            else:
                st.caption("None detected.")
        with fc2:
            st.markdown("#### ⚠️ Aggravating Factors")
            if aggravators:
                for a in aggravators:
                    st.markdown(f"- {a}")
            else:
                st.caption("None detected.")

        st.markdown("---")
        st.markdown("### 👤 Human-in-the-Loop Override")
        override = st.radio(
            "Final decision (Loan Officer):",
            options=[f"Accept agent recommendation ({decision})",
                     "Override → APPROVE", "Override → DENY"],
            horizontal=True,
        )
        officer_note = st.text_input("Officer note (optional)",
                                       placeholder="Reason for override or special instruction...")
        final_decision = decision
        if "APPROVE" in override and decision != "APPROVE":
            final_decision = "APPROVE"
        elif "DENY" in override and decision != "DENY":
            final_decision = "DENY"

        st.markdown("---")
        st.markdown("### ✉️ Decision Letter to Borrower")
        letter = generate_letter(name, final_decision, prob_paid,
                                  mitigators, aggravators, Loan_Amount, officer_note)
        st.markdown(letter)
        st.download_button(
            "📥 Download letter (Markdown)",
            data=letter,
            file_name=f"decision_letter_{name.replace(' ', '_')}.md",
            mime="text/markdown",
        )

        with st.expander("🧾 Audit trail (JSON)"):
            audit = {
                "timestamp": datetime.now().isoformat(),
                "applicant": name,
                "model": meta['winning_model'],
                "prob_default": round(prob_default, 4),
                "prob_paid": round(prob_paid, 4),
                "agent_recommendation": decision,
                "final_decision": final_decision,
                "officer_overrode": final_decision != decision,
                "officer_note": officer_note,
                "mitigating_factors": mitigators,
                "aggravating_factors": aggravators,
                "borrower_features": intake,
            }
            st.json(audit)
