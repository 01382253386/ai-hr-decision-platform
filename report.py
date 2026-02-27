from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


# ─────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────
DARK_BG     = colors.HexColor("#1a1a2e")
BLUE        = colors.HexColor("#4f8ef7")
LIGHT_BLUE  = colors.HexColor("#e8f0fe")
RED         = colors.HexColor("#ff4b4b")
ORANGE      = colors.HexColor("#ff8c00")
GREEN       = colors.HexColor("#00c851")
YELLOW      = colors.HexColor("#ffd700")
DARK_TEXT   = colors.HexColor("#1a1a2e")
GREY        = colors.HexColor("#666666")
LIGHT_GREY  = colors.HexColor("#f5f5f5")
WHITE       = colors.white


def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontSize=26, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontSize=12, fontName="Helvetica",
        textColor=colors.HexColor("#aaaacc"), alignment=TA_CENTER,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=14, fontName="Helvetica-Bold",
        textColor=BLUE, spaceBefore=16, spaceAfter=8,
        borderPad=4
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontSize=10, fontName="Helvetica",
        textColor=DARK_TEXT, spaceAfter=4, leading=16
    ))
    styles.add(ParagraphStyle(
        name="SmallGrey",
        fontSize=8, fontName="Helvetica",
        textColor=GREY, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name="BulletText",
        fontSize=10, fontName="Helvetica",
        textColor=DARK_TEXT, spaceAfter=3,
        leftIndent=12, leading=15
    ))
    styles.add(ParagraphStyle(
        name="RecommendBox",
        fontSize=11, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="BiasFlag",
        fontSize=10, fontName="Helvetica",
        textColor=DARK_TEXT, spaceAfter=3, leading=15
    ))
    return styles


def severity_color(severity):
    s = str(severity).lower()
    if s == "critical": return RED
    if s == "high":     return RED
    if s == "medium":   return ORANGE
    if s == "low":      return GREEN
    return GREY


def risk_color(risk):
    r = str(risk).lower()
    if r == "critical": return RED
    if r == "high":     return RED
    if r == "medium":   return ORANGE
    if r == "low":      return GREEN
    return GREY


def generate_report(
    problem_text: str = "",
    problem_analysis: dict = None,
    candidates: list = None,
    scoring_result: dict = None,
    bias_result: dict = None,
    decision_result: dict = None
) -> bytes:
    """
    Generate a CEO-ready PDF report.
    Returns PDF as bytes — can be streamed directly from FastAPI.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = get_styles()
    story = []
    W = A4[0] - 4*cm  # usable width

    # ─────────────────────────────────────────────
    # PAGE 1 — COVER + DECISION SUMMARY
    # ─────────────────────────────────────────────

    # Dark header banner
    header_data = [[
        Paragraph("⚡ AI HR DECISION PLATFORM", styles["ReportTitle"]),
    ]]
    header_table = Table(header_data, colWidths=[W])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
        ("TOPPADDING", (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Executive Decision Report  |  Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
        styles["SmallGrey"]
    ))
    story.append(Spacer(1, 10))

    # RECOMMENDED ACTION BOX
    if decision_result:
        decision = decision_result.get("decision", "PENDING")
        candidate = decision_result.get("candidate", "Unknown")
        reasoning = decision_result.get("reasoning", "")
        rec = decision_result.get("recommendation", "")
        box_color = GREEN if "APPROVE" in str(decision).upper() else RED

        rec_data = [[
            Paragraph(f"RECOMMENDED ACTION: {decision} — {candidate}", styles["RecommendBox"])
        ]]
        rec_table = Table(rec_data, colWidths=[W])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), box_color),
            ("TOPPADDING", (0,0), (-1,-1), 14),
            ("BOTTOMPADDING", (0,0), (-1,-1), 14),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ("ROUNDEDCORNERS", [6]),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 8))

        if reasoning:
            story.append(Paragraph(f"<b>Reasoning:</b> {reasoning}", styles["BodyText2"]))
        if rec:
            story.append(Paragraph(f"<b>Next Step:</b> {rec}", styles["BodyText2"]))
        story.append(Spacer(1, 10))

    # PROBLEM ANALYSIS
    if problem_analysis:
        story.append(HRFlowable(width=W, color=BLUE, thickness=1))
        story.append(Paragraph("Problem Analysis", styles["SectionHeader"]))

        urgency = problem_analysis.get("urgency", "unknown").upper()
        p_type  = problem_analysis.get("problem_type", "unknown").title()
        b_need  = problem_analysis.get("business_need", "")

        meta_data = [
            [Paragraph("<b>Urgency</b>", styles["BodyText2"]),
             Paragraph("<b>Type</b>", styles["BodyText2"]),
             Paragraph("<b>Business Need</b>", styles["BodyText2"])],
            [Paragraph(urgency, styles["BodyText2"]),
             Paragraph(p_type, styles["BodyText2"]),
             Paragraph(b_need, styles["BodyText2"])]
        ]
        meta_table = Table(meta_data, colWidths=[W*0.15, W*0.15, W*0.70])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), LIGHT_BLUE),
            ("BACKGROUND", (0,1), (-1,1), WHITE),
            ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("TEXTCOLOR", (0,1), (0,1), risk_color(urgency)),
            ("FONTNAME", (0,1), (0,1), "Helvetica-Bold"),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 8))

        constraints = problem_analysis.get("constraints", [])
        hidden_risks = problem_analysis.get("hidden_risks", [])
        goals = problem_analysis.get("success_goals", [])

        col1_content = []
        col2_content = []

        if constraints:
            col1_content.append(Paragraph("<b>Constraints</b>", styles["BodyText2"]))
            for c in constraints:
                col1_content.append(Paragraph(f"• {c}", styles["BulletText"]))

        if goals:
            col1_content.append(Spacer(1,6))
            col1_content.append(Paragraph("<b>Success Goals</b>", styles["BodyText2"]))
            for g in goals:
                col1_content.append(Paragraph(f"• {g}", styles["BulletText"]))

        if hidden_risks:
            col2_content.append(Paragraph("<b>Hidden Risks Identified by AI</b>", styles["BodyText2"]))
            for r in hidden_risks:
                col2_content.append(Paragraph(f"⚠ {r}", styles["BulletText"]))

        two_col = Table(
            [[col1_content, col2_content]],
            colWidths=[W*0.48, W*0.48]
        )
        two_col.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(two_col)

    story.append(PageBreak())

    # ─────────────────────────────────────────────
    # PAGE 2 — CANDIDATE RANKING
    # ─────────────────────────────────────────────
    story.append(Paragraph("Candidate Ranking", styles["SectionHeader"]))
    story.append(HRFlowable(width=W, color=BLUE, thickness=1))
    story.append(Spacer(1, 8))

    if scoring_result:
        ranking = scoring_result.get("ranking", [])
        role_type = scoring_result.get("role_type", "technical").title()
        story.append(Paragraph(f"Role Type: <b>{role_type}</b>", styles["BodyText2"]))
        story.append(Spacer(1, 8))

        if ranking:
            table_data = [[
                Paragraph("<b>Rank</b>", styles["BodyText2"]),
                Paragraph("<b>Candidate</b>", styles["BodyText2"]),
                Paragraph("<b>Score</b>", styles["BodyText2"]),
                Paragraph("<b>Confidence</b>", styles["BodyText2"]),
                Paragraph("<b>Top Strength</b>", styles["BodyText2"]),
                Paragraph("<b>Top Risk</b>", styles["BodyText2"]),
            ]]
            medals = ["1st", "2nd", "3rd"]
            for i, c in enumerate(ranking):
                rank = medals[i] if i < 3 else f"#{i+1}"
                score = c.get("score", 0)
                table_data.append([
                    Paragraph(rank, styles["BodyText2"]),
                    Paragraph(str(c.get("name","")), styles["BodyText2"]),
                    Paragraph(f"{score}/100", styles["BodyText2"]),
                    Paragraph(str(c.get("confidence","")), styles["BodyText2"]),
                    Paragraph(str(c.get("top_strength","")).replace("_"," ").title(), styles["BodyText2"]),
                    Paragraph(str(c.get("top_risk","")).replace("_"," ").title(), styles["BodyText2"]),
                ])

            rank_table = Table(table_data, colWidths=[
                W*0.08, W*0.22, W*0.12, W*0.14, W*0.22, W*0.22
            ])
            rank_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), DARK_BG),
                ("TEXTCOLOR", (0,0), (-1,0), WHITE),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GREY]),
                ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
                ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
                ("TOPPADDING", (0,0), (-1,-1), 7),
                ("BOTTOMPADDING", (0,0), (-1,-1), 7),
                ("LEFTPADDING", (0,0), (-1,-1), 8),
                ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#e8f5e9")),
            ]))
            story.append(rank_table)
            story.append(Spacer(1, 10))

        # Weights used
        weights = scoring_result.get("weights_used", {})
        if weights:
            story.append(Paragraph("<b>Scoring Weights Used</b>", styles["BodyText2"]))
            w_data = [[Paragraph(f"<b>{k.replace('_',' ').title()}</b>", styles["SmallGrey"])
                       for k in weights.keys()]]
            w_data.append([Paragraph(f"{int(v*100)}%", styles["BodyText2"])
                           for v in weights.values()])
            w_table = Table(w_data, colWidths=[W/len(weights)]*len(weights))
            w_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), LIGHT_BLUE),
                ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
                ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
                ("TOPPADDING", (0,0), (-1,-1), 5),
                ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                ("LEFTPADDING", (0,0), (-1,-1), 6),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ]))
            story.append(w_table)

        # Bias audit on scoring
        bias_audit = scoring_result.get("bias_audit", {})
        if bias_audit and "error" not in bias_audit:
            story.append(Spacer(1, 10))
            story.append(Paragraph("Scoring Bias Audit", styles["SectionHeader"]))
            b_risk = bias_audit.get("scoring_bias_risk", "unknown").upper()
            story.append(Paragraph(
                f"Scoring Bias Risk: <b>{b_risk}</b>",
                styles["BodyText2"]
            ))
            for w in bias_audit.get("bias_warnings", []):
                story.append(Paragraph(f"⚠ {w}", styles["BulletText"]))
            rec = bias_audit.get("recommendation", "")
            if rec:
                story.append(Paragraph(f"Recommendation: {rec}", styles["BodyText2"]))

    story.append(PageBreak())

    # ─────────────────────────────────────────────
    # PAGE 3 — BIAS ANALYSIS
    # ─────────────────────────────────────────────
    story.append(Paragraph("Bias Analysis Report", styles["SectionHeader"]))
    story.append(HRFlowable(width=W, color=BLUE, thickness=1))
    story.append(Spacer(1, 8))

    if bias_result and "error" not in bias_result:
        overall = bias_result.get("overall_bias_risk", "unknown").upper()
        score   = bias_result.get("bias_score", 0)
        comp    = bias_result.get("compliance_risk", "unknown").upper()
        comp_note = bias_result.get("compliance_note", "")

        summary_data = [
            [Paragraph("<b>Overall Bias Risk</b>", styles["BodyText2"]),
             Paragraph("<b>Bias Score</b>", styles["BodyText2"]),
             Paragraph("<b>Compliance Risk</b>", styles["BodyText2"])],
            [Paragraph(overall, styles["BodyText2"]),
             Paragraph(f"{score}/100", styles["BodyText2"]),
             Paragraph(comp, styles["BodyText2"])]
        ]
        s_table = Table(summary_data, colWidths=[W/3]*3)
        s_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), LIGHT_BLUE),
            ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("TEXTCOLOR", (0,1), (0,1), risk_color(overall)),
            ("TEXTCOLOR", (1,1), (1,1), risk_color(overall)),
            ("TEXTCOLOR", (2,1), (2,1), risk_color(comp)),
            ("FONTNAME", (0,1), (-1,1), "Helvetica-Bold"),
        ]))
        story.append(s_table)
        story.append(Spacer(1, 10))

        flags = bias_result.get("flags", [])
        if flags:
            story.append(Paragraph(f"<b>{len(flags)} Bias Flags Detected</b>", styles["BodyText2"]))
            story.append(Spacer(1, 6))

            for flag in flags:
                sev = flag.get("severity", "low")
                f_color = severity_color(sev)
                flag_data = [[
                    Paragraph(
                        f"<b>{flag.get('type','Unknown')} — {sev.upper()}</b><br/>"
                        f"Trigger: \"{flag.get('trigger_text','')}\"<br/>"
                        f"Why: {flag.get('explanation','')}<br/>"
                        f"Fix: {flag.get('suggested_fix','')}",
                        styles["BiasFlag"]
                    )
                ]]
                f_table = Table(flag_data, colWidths=[W])
                f_table.setStyle(TableStyle([
                    ("LEFTPADDING", (0,0), (-1,-1), 10),
                    ("TOPPADDING", (0,0), (-1,-1), 8),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                    ("LINEBEFORE", (0,0), (0,-1), 4, f_color),
                    ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
                    ("BOX", (0,0), (-1,-1), 0.3, colors.HexColor("#cccccc")),
                ]))
                story.append(f_table)
                story.append(Spacer(1, 4))

        if comp_note:
            story.append(Spacer(1, 6))
            story.append(Paragraph("Legal / Compliance Note", styles["SectionHeader"]))
            story.append(Paragraph(comp_note, styles["BodyText2"]))

        clean = bias_result.get("clean_summary", "")
        if clean:
            story.append(Spacer(1, 8))
            story.append(Paragraph("Bias-Free Rewrite", styles["SectionHeader"]))
            story.append(Paragraph(clean, styles["BodyText2"]))

    else:
        story.append(Paragraph("No bias analysis data provided.", styles["BodyText2"]))

    story.append(PageBreak())

    # ─────────────────────────────────────────────
    # PAGE 4 — RISK ASSESSMENT + FOOTER
    # ─────────────────────────────────────────────
    story.append(Paragraph("Risk Assessment & Recommendations", styles["SectionHeader"]))
    story.append(HRFlowable(width=W, color=BLUE, thickness=1))
    story.append(Spacer(1, 8))

    risk_items = []
    if problem_analysis:
        for r in problem_analysis.get("hidden_risks", []):
            risk_items.append(("AI-Identified Risk", r, "medium"))
    if bias_result and "error" not in bias_result:
        for f in bias_result.get("flags", []):
            risk_items.append(("Bias Risk", f.get("type",""), f.get("severity","low")))

    if risk_items:
        risk_data = [[
            Paragraph("<b>Category</b>", styles["BodyText2"]),
            Paragraph("<b>Risk</b>", styles["BodyText2"]),
            Paragraph("<b>Severity</b>", styles["BodyText2"]),
        ]]
        for cat, desc, sev in risk_items:
            risk_data.append([
                Paragraph(cat, styles["BodyText2"]),
                Paragraph(str(desc), styles["BodyText2"]),
                Paragraph(str(sev).upper(), styles["BodyText2"]),
            ])
        r_table = Table(risk_data, colWidths=[W*0.22, W*0.55, W*0.23])
        r_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), DARK_BG),
            ("TEXTCOLOR", (0,0), (-1,0), WHITE),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GREY]),
            ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(r_table)
    else:
        story.append(Paragraph("No significant risks identified.", styles["BodyText2"]))

    story.append(Spacer(1, 20))

    # Footer
    footer_data = [[Paragraph(
        f"AI HR Decision Platform  |  Confidential  |  {datetime.now().strftime('%d %b %Y')}  |  "
        "This report was generated by AI and should be reviewed by a qualified HR professional.",
        styles["SmallGrey"]
    )]]
    footer_table = Table(footer_data, colWidths=[W])
    footer_table.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("LINEABOVE", (0,0), (-1,0), 0.5, GREY),
    ]))
    story.append(footer_table)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
