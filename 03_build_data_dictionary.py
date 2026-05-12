"""Build Data Dictionary PDF for the new schema."""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_CENTER

OUT = '/home/claude/v2/Data_Dictionary.pdf'
doc = SimpleDocTemplate(OUT, pagesize=letter,
                        leftMargin=0.45*inch, rightMargin=0.45*inch,
                        topMargin=0.4*inch, bottomMargin=0.4*inch)
styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=15,
                              textColor=colors.HexColor('#0A2540'),
                              alignment=TA_CENTER, spaceAfter=2)
sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9,
                            textColor=colors.HexColor('#5A6F87'),
                            alignment=TA_CENTER, spaceAfter=10)
section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=11,
                                textColor=colors.HexColor('#1E4D7B'),
                                spaceBefore=8, spaceAfter=4)
body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=8.5, leading=11)

story = []
story.append(Paragraph("APEX GLOBAL BANK — Data Dictionary", title_style))
story.append(Paragraph(
    "Emerging Market Entrepreneurs Loan Product · 1,000 borrowers · 20 features + 1 target",
    sub_style))

story.append(Paragraph("Why this feature mix?", section_style))
story.append(Paragraph(
    "Emerging-market entrepreneurs typically have <b>thin traditional credit files</b>. "
    "Standard models that lean on credit score, income, and collateral systematically "
    "decline creditworthy borrowers from this segment. We balanced <b>10 traditional</b> "
    "and <b>10 behavioral</b> features so the model can detect creditworthiness through "
    "patterns of <i>behavior</i> — bill consistency, savings habits, community engagement, "
    "app activity, and network quality — which legacy scorecards ignore.",
    body_style))

def make_table(title, rows):
    story.append(Paragraph(title, section_style))
    table_data = [['Variable', 'Type', 'Description & rationale']]
    for r in rows:
        table_data.append([
            Paragraph(f"<b>{r[0]}</b>", body_style),
            Paragraph(r[1], body_style),
            Paragraph(r[2], body_style),
        ])
    t = Table(table_data, colWidths=[1.45*inch, 0.65*inch, 5.5*inch], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0A2540')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
            [colors.HexColor('#F5F7FA'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CCCCCC')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)

traditional = [
    ('Age', 'int', "Borrower age (18–70). Proxy for life-stage financial stability."),
    ('Monthly_Income', 'float', "Self-reported monthly income in USD ($430–$25,000). Lognormal spread typical of emerging markets."),
    ('Debt_to_Income', 'float', "Ratio of existing debt to income (0.05–0.92). Strong traditional risk indicator."),
    ('Credit_Score', 'int', "Bureau score (300–850). Industry standard; weak alone for thin-file borrowers but informative when combined."),
    ('Loan_Amount', 'float', "Requested principal in USD ($5,500–$90,000). Higher principal = larger exposure on default."),
    ('Employment_Years', 'float', "Tenure at current employer. Longer tenure → cash-flow predictability."),
    ('Dependants', 'int', "Household dependants (0–7). Higher count strains disposable income."),
    ('Prior_Defaults', 'int', "Past defaults on record (0–5). Strongest single traditional risk flag."),
    ('Collateral_Value', 'float', "Value of pledged collateral in USD. Recovers principal on default."),
    ('Credit_Accounts', 'int', "Number of active credit accounts. Thin-file proxy."),
]
make_table("Traditional features (10)", traditional)

behavioral = [
    ('Utility_Latency', 'float', "Avg days late on utility bills (0–45). Direct behavioral signal of payment discipline."),
    ('App_Session_Time', 'float', "Minutes spent in the banking app per month. Proxy for financial attention."),
    ('Social_Sentiment', 'float', "Sentiment score from anonymized social/community signals (−1 to +1). Reputation proxy."),
    ('Mobile_Data_Use', 'float', "Mobile data usage (GB/month). Digital-economy participation."),
    ('Ecommerce_Freq', 'int', "E-commerce purchases per month. Diversified spending = broader engagement."),
    ('Savings_Score', 'float', "Composite savings discipline score (0–100). Indicates buffer capacity."),
    ('Community_Score', 'float', "Reputation/standing in local community (0–100). Soft trust signal."),
    ('Night_Activity', 'float', "Share of activity at night (0–1). High values can indicate irregular cash patterns."),
    ('Contact_Diversity', 'int', "Distinct transaction/contact counterparties. Network-quality proxy."),
    ('Bill_Consistency', 'float', "Consistency of bill payments (0–1). High = predictable, low = erratic."),
]
make_table("Behavioral features (10)", behavioral)

story.append(Paragraph("Target variable & ethical notes", section_style))
story.append(Paragraph(
    "<b>Loan_Status</b> (binary): <b>0</b> = Default, <b>1</b> = Paid. "
    "Base default rate ≈ <b>20%</b> in the dataset. "
    "<b>Bias guardrails</b>: we exclude all protected attributes (gender, ethnicity, religion). "
    "The agent always surfaces mitigating factors and routes Grey-Zone cases to a human "
    "loan officer — humans hold the final decision. Every decision is logged with a full audit trail.",
    body_style))

doc.build(story)
print(f"✓ Built {OUT}")
