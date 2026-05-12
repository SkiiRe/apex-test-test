"""Train 3 models, evaluate at decision threshold 0.65 to expose differences."""
import json, joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, confusion_matrix, roc_curve

THRESHOLD = 0.65
OUT = Path('/home/claude/v2')
df = pd.read_csv(OUT / 'borrower_data.csv')
print(f"Rows: {len(df)}  Default rate: {(df['Loan_Status']==0).mean():.1%}")

y = df['Loan_Status']
X = df.drop(columns=['Loan_Status'])
numeric_cols = X.columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)

pre_scaled = ColumnTransformer([('num', StandardScaler(), numeric_cols)])
pre_unscaled = ColumnTransformer([('num', 'passthrough', numeric_cols)])

models = {
    'Logistic Regression': Pipeline([
        ('pre', pre_scaled),
        ('clf', LogisticRegression(max_iter=2000, class_weight='balanced',
                                   solver='liblinear', random_state=42))
    ]),
    'Decision Tree': Pipeline([
        ('pre', pre_unscaled),
        ('clf', DecisionTreeClassifier(max_depth=3, min_samples_leaf=40,
                                       class_weight='balanced', random_state=42))
    ]),
    'Random Forest': Pipeline([
        ('pre', pre_unscaled),
        ('clf', RandomForestClassifier(n_estimators=200, max_depth=6,
                                       min_samples_leaf=15, n_jobs=-1,
                                       class_weight='balanced', random_state=42))
    ]),
}

def profitability(y_true, y_pred, test_df):
    profit = 0.0
    tp_count = fp_count = 0
    for actual, pred, principal in zip(y_true, y_pred, test_df['Loan_Amount'].values):
        if pred == 1 and actual == 1:
            profit += principal * 0.18 * 2
            tp_count += 1
        elif pred == 1 and actual == 0:
            profit -= principal
            fp_count += 1
    return profit, tp_count, fp_count

results, roc_data, fitted = [], {}, {}

for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    fitted[name] = pipe
    y_proba = pipe.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= THRESHOLD).astype(int)
    auc = roc_auc_score(y_test, y_proba)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    fpr_bank = fp / (fp + tn) if (fp + tn) else 0.0
    acc = (tp + tn) / (tp + tn + fp + fn)
    profit, n_tp, n_fp = profitability(y_test.values, y_pred, X_test)
    fpr_c, tpr_c, _ = roc_curve(y_test, y_proba)
    roc_data[name] = (fpr_c, tpr_c, auc)
    results.append({
        'Model': name, 'AUC_ROC': round(auc, 3),
        'Accuracy': round(acc, 3),
        'False_Positive_Rate': round(fpr_bank, 3),
        'Profitability_USD': round(profit, 0),
        'TP': int(tp), 'FP': int(fp), 'TN': int(tn), 'FN': int(fn),
    })

res = pd.DataFrame(results).set_index('Model')
print("\n" + "="*78)
print(res.to_string())
winner = res['Profitability_USD'].idxmax()
print(f"\nWINNER: {winner}  |  ${res.loc[winner,'Profitability_USD']:,.0f}")

# Charts
plt.figure(figsize=(7, 6))
for name, (fpr, tpr, auc) in roc_data.items():
    plt.plot(fpr, tpr, linewidth=2, label=f'{name} (AUC = {auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', alpha=0.4)
plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate')
plt.title('ROC Curves — Credit Default Models', fontweight='bold')
plt.legend(loc='lower right'); plt.grid(alpha=0.3); plt.tight_layout()
plt.savefig(OUT / 'roc_curves.png', dpi=150, bbox_inches='tight'); plt.close()

rf = fitted['Random Forest']
imp_df = pd.DataFrame({'feature': numeric_cols,
                        'importance': rf.named_steps['clf'].feature_importances_})
imp_df = imp_df.sort_values('importance').tail(15)
plt.figure(figsize=(9, 6))
plt.barh(imp_df['feature'], imp_df['importance'], color='#2E75B6')
plt.xlabel('Importance'); plt.title('Top 15 Features — Random Forest', fontweight='bold')
plt.tight_layout(); plt.savefig(OUT / 'feature_importance.png', dpi=150,
                                  bbox_inches='tight'); plt.close()

plt.figure(figsize=(8, 5))
colors = ['#C00000' if m != winner else '#2E7D32' for m in res.index]
bars = plt.bar(res.index, res['Profitability_USD'], color=colors)
plt.ylabel('Portfolio Profit (USD)')
plt.title('Profitability Index — Test Portfolio', fontweight='bold')
for bar, val in zip(bars, res['Profitability_USD']):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f'${val:,.0f}', ha='center', va='bottom')
plt.grid(axis='y', alpha=0.3); plt.tight_layout()
plt.savefig(OUT / 'profitability.png', dpi=150, bbox_inches='tight'); plt.close()

joblib.dump(fitted[winner], OUT / 'best_model.joblib')
meta = {
    'winning_model': winner,
    'decision_threshold': THRESHOLD,
    'metrics': res.loc[winner].to_dict(),
    'features': X.columns.tolist(),
    'numeric_features': numeric_cols,
    'training_default_rate': float((y == 0).mean()),
    'feature_ranges': {
        c: {'min': float(X[c].min()), 'max': float(X[c].max()),
            'median': float(X[c].median())}
        for c in numeric_cols
    },
}
with open(OUT / 'model_meta.json', 'w') as f:
    json.dump(meta, f, indent=2)
res.to_csv(OUT / 'model_dashboard.csv')
print("\n✓ All saved")
