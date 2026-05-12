# 🏦 Apex Credit Sentinel™

**Agentic AI Credit Officer for Emerging Market Entrepreneurs**

## What's here

| File | Purpose |
|------|---------|
| `app.py` | The Streamlit AI agent (the live demo) |
| `borrower_data.csv` | The dataset — 1,000 borrowers, 20 features |
| `02_train_models.py` | Trains the 3 models (run once) |
| `03_build_data_dictionary.py` | Builds Data_Dictionary.pdf |
| `04_build_model_report.py` | Builds Model_Report.pdf |
| `apex_pipeline.R` | Full R pipeline for RStudio |
| `best_model.joblib` | The trained winner — Logistic Regression |
| `model_meta.json` | Model metadata |
| `Data_Dictionary.pdf` | 📄 Deliverable #1 |
| `Model_Report.pdf` | 📄 Deliverable #2 |
| `PITCH.md` | 5-minute pitch script |
| `requirements.txt` | For Streamlit Cloud |

## Deploy on Streamlit Cloud (5 min)

1. Push this folder to a public GitHub repo
2. Go to https://share.streamlit.io → New app
3. Pick the repo, branch `main`, main file `app.py` → Deploy

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run R pipeline in RStudio

Put `borrower_data.csv` and `apex_pipeline.R` in the same folder, open the R file in RStudio, hit **Ctrl+Shift+Enter**.

## Demo flow

1. Open the deployed URL
2. Sidebar → **🟢 Maria** → Run → AUTO-APPROVE
3. Sidebar → **🔴 Carlos** → Run → AUTO-DENY
4. Sidebar → **🟡 Amara (⭐ Pitch demo)** → Run → **GREY ZONE → Conditional Approval** ← the money shot
