import streamlit as st
import requests
import json

st.set_page_config(
    page_title="AI HR Decision Platform",
    page_icon="⚡",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stButton>button {
        background-color: #4f8ef7;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    .stButton>button:hover { background-color: #2f6ed4; }
    .bias-high   { border-left: 4px solid #ff4b4b; background: #fff0f0; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }
    .bias-medium { border-left: 4px solid #ff8c00; background: #fff8f0; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }
    .bias-low    { border-left: 4px solid #00c851; background: #f0fff4; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("# ⚡ AI HR Decision Platform")
st.markdown("**Bias-aware hiring decisions powered by Claude AI**")
st.markdown("---")

# ── SIDEBAR ──────────────────────────────────
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    page = st.radio("Choose a module:", [
        "🔍 Analyse Problem",
        "👥 Score Candidates",
        "✅ Create Decision",
        "🚨 Detect Bias",
        "📊 Audit Decisions",
        "📄 Download PDF Report"
    ])
    st.markdown("---")
    st.markdown("### Server Status")
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        if r.status_code == 200:
            st.success("🟢 API Connected")
            st.caption(f"Version: {r.json().get('version','?')}")
    except:
        st.error("🔴 API Not Running")
        st.caption("Run: uvicorn main:app --reload")

# ── PAGE 1 — ANALYSE PROBLEM ─────────────────
if page == "🔍 Analyse Problem":
    st.markdown("## 🔍 Analyse HR Problem")
    st.markdown("Paste any HR problem in plain English. AI will extract urgency, constraints, goals and hidden risks.")

    problem = st.text_area("Describe your HR problem:", height=150,
        placeholder="Example: Our tech lead just resigned and we need to hire a replacement urgently...")

    if st.button("🔍 Analyse Problem"):
        if not problem.strip():
            st.warning("Please enter a problem description.")
        else:
            with st.spinner("Analysing with Claude AI..."):
                try:
                    r = requests.post(f"{API_URL}/analyse-problem", json={"problem": problem})
                    result = r.json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.markdown("---")
                        st.markdown("### 📋 Analysis Results")
                        col1, col2, col3 = st.columns(3)
                        urgency = result.get("urgency","unknown").upper()
                        icon = {"LOW":"🟢","MEDIUM":"🟡","HIGH":"🔴"}.get(urgency,"⚪")
                        with col1: st.metric("Urgency", f"{icon} {urgency}")
                        with col2: st.metric("Problem Type", result.get("problem_type","?").title())
                        with col3: st.metric("Constraints Found", len(result.get("constraints",[])))

                        st.info(f"**Business Need:** {result.get('business_need','')}")

                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("**⛔ Constraints**")
                            for c in result.get("constraints",[]): st.markdown(f"• {c}")
                            st.markdown("**🎯 Success Goals**")
                            for g in result.get("success_goals",[]): st.markdown(f"• {g}")
                        with col_b:
                            st.markdown("**⚠️ Hidden Risks**")
                            for risk in result.get("hidden_risks",[]): st.warning(f"⚠️ {risk}")

                        st.session_state["problem_text"]     = problem
                        st.session_state["problem_analysis"] = result
                except Exception as e:
                    st.error(f"Could not connect to API.\nError: {e}")

# ── PAGE 2 — SCORE CANDIDATES ────────────────
elif page == "👥 Score Candidates":
    st.markdown("## 👥 Score Candidates")
    role_type = st.selectbox("Role Type:", ["technical", "executive", "operational"])
    num = st.number_input("How many candidates?", min_value=1, max_value=3, value=2)

    candidates = []
    for i in range(int(num)):
        st.markdown(f"### Candidate {i+1}")
        c1, c2 = st.columns(2)
        with c1:
            name  = st.text_input("Name", key=f"n{i}", placeholder=f"Candidate {i+1}")
            skill = st.slider("Skill Match",     1, 5, 3, key=f"s{i}")
            cult  = st.slider("Culture Fit",     1, 5, 3, key=f"c{i}")
        with c2:
            spd   = st.slider("Execution Speed", 1, 5, 3, key=f"e{i}")
            cost  = st.slider("Cost Efficiency", 1, 5, 3, key=f"co{i}")
            adpt  = st.slider("Adaptability",    1, 5, 3, key=f"a{i}")
        if name:
            candidates.append({"name":name,"skill_match":skill,"culture_fit":cult,
                                "execution_speed":spd,"cost_efficiency":cost,"adaptability":adpt})
        st.markdown("---")

    if st.button("📊 Score All Candidates"):
        if not candidates:
            st.warning("Enter at least one candidate name.")
        else:
            with st.spinner("Scoring..."):
                try:
                    r = requests.post(f"{API_URL}/bias-score-candidates",
                                      json={"candidates": candidates, "role_type": role_type})
                    result = r.json()
                    st.markdown("### 🏆 Ranking")
                    for idx, c in enumerate(result.get("ranking",[])):
                        medal = ["🥇","🥈","🥉"][idx] if idx < 3 else f"#{idx+1}"
                        c1,c2,c3,c4 = st.columns(4)
                        with c1: st.metric(f"{medal} {c['name']}", f"{c['score']}/100")
                        with c2: st.metric("Confidence", c['confidence'])
                        with c3: st.metric("Strength", c['top_strength'].replace("_"," ").title())
                        with c4: st.metric("Risk", c['top_risk'].replace("_"," ").title())

                    ba = result.get("bias_audit",{})
                    if ba and "error" not in ba:
                        st.markdown("---")
                        st.markdown("### 🚨 Scoring Bias Audit")
                        risk = ba.get("scoring_bias_risk","?")
                        icon = {"low":"🟢","medium":"🟡","high":"🔴"}.get(risk,"⚪")
                        st.markdown(f"**Bias Risk: {icon} {risk.upper()}**")
                        for w in ba.get("bias_warnings",[]): st.warning(f"⚠️ {w}")
                        if ba.get("recommendation"): st.info(f"💡 {ba['recommendation']}")

                    st.session_state["scoring_result"] = result
                    st.session_state["candidates"]     = candidates
                except Exception as e:
                    st.error(f"API error: {e}")

# ── PAGE 3 — CREATE DECISION ─────────────────
elif page == "✅ Create Decision":
    st.markdown("## ✅ Create Hiring Decision")
    c1, c2 = st.columns(2)
    with c1:
        name  = st.text_input("Candidate Name", placeholder="e.g. Sarah Johnson")
        pos   = st.text_input("Position",        placeholder="e.g. Senior Engineer")
        exp   = st.number_input("Years Experience", 0, 50, 5)
    with c2:
        skills_raw = st.text_area("Skills (one per line)", height=120,
                                  placeholder="Python\nFastAPI\nLeadership")
        notes = st.text_area("Interview Notes", height=80)

    if st.button("✅ Make Decision"):
        if not name or not pos:
            st.warning("Enter candidate name and position.")
        else:
            skills = [s.strip() for s in skills_raw.split("\n") if s.strip()] or ["Not specified"]
            with st.spinner("Evaluating..."):
                try:
                    r = requests.post(f"{API_URL}/create-decision",
                        json={"candidate_name":name,"position":pos,
                              "experience_years":exp,"skills":skills,"notes":notes})
                    result = r.json()
                    st.markdown("---")
                    decision = result.get("decision","?")
                    c1,c2,c3 = st.columns(3)
                    with c1:
                        if "APPROVE" in decision.upper(): st.success(f"✅ {decision}")
                        else: st.error(f"❌ {decision}")
                    with c2: st.metric("Confidence", result.get("confidence","?"))
                    with c3: st.metric("Candidate",  name)
                    st.info(f"**Reasoning:** {result.get('reasoning','')}")
                    st.success(f"**Next Step:** {result.get('recommendation','')}")
                    st.session_state["decision_result"] = result
                except Exception as e:
                    st.error(f"API error: {e}")

# ── PAGE 4 — DETECT BIAS ─────────────────────
elif page == "🚨 Detect Bias":
    st.markdown("## 🚨 Bias Detection Engine")
    t1, t2, t3 = st.tabs(["📄 Job Description","🗒️ Interview Notes","🧠 Decision Reasoning"])
    with t1: job_desc = st.text_area("Job description:", height=150,
        placeholder="We need a young energetic rockstar developer...")
    with t2: interview = st.text_area("Interview notes:", height=150,
        placeholder="He seemed very confident. The female candidate felt too aggressive...")
    with t3: reasoning = st.text_area("Decision reasoning:", height=150,
        placeholder="We rejected her because she didn't seem like a culture fit...")

    if st.button("🚨 Scan for Bias"):
        if not job_desc and not interview and not reasoning:
            st.warning("Enter at least one field.")
        else:
            with st.spinner("Scanning with Claude AI..."):
                try:
                    r = requests.post(f"{API_URL}/detect-bias",
                        json={"job_description": job_desc or None,
                              "interview_notes": interview or None,
                              "decision_reasoning": reasoning or None})
                    result = r.json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.markdown("---")
                        overall = result.get("overall_bias_risk","?").upper()
                        score   = result.get("bias_score", 0)
                        comp    = result.get("compliance_risk","?").upper()
                        icons   = {"LOW":"🟢","MEDIUM":"🟡","HIGH":"🔴","CRITICAL":"🚨"}
                        c1,c2,c3 = st.columns(3)
                        with c1: st.metric("Overall Bias Risk", f"{icons.get(overall,'⚪')} {overall}")
                        with c2: st.metric("Bias Score",        f"{score}/100")
                        with c3: st.metric("Compliance Risk",   f"{icons.get(comp,'⚪')} {comp}")

                        flags = result.get("flags",[])
                        if flags:
                            st.markdown(f"### 🚩 {len(flags)} Flags Found")
                            for f in flags:
                                sev  = f.get("severity","low")
                                icon = {"low":"🟡","medium":"🟠","high":"🔴"}.get(sev,"⚪")
                                st.markdown(f"""<div class="bias-{sev}">
                                    <b>{icon} {f.get('type','')} — {sev.upper()}</b><br>
                                    <em>Trigger: "{f.get('trigger_text','')}"</em><br><br>
                                    <b>Why:</b> {f.get('explanation','')}<br>
                                    <b>✅ Fix:</b> {f.get('suggested_fix','')}
                                </div>""", unsafe_allow_html=True)
                        else:
                            st.success("✅ No bias flags detected.")

                        if result.get("compliance_note"):
                            st.warning(f"⚖️ {result['compliance_note']}")
                        if result.get("clean_summary"):
                            st.markdown("### ✅ Bias-Free Rewrite")
                            st.success(result["clean_summary"])

                        st.session_state["bias_result"] = result
                except Exception as e:
                    st.error(f"API error: {e}")

# ── PAGE 5 — AUDIT DECISIONS ─────────────────
elif page == "📊 Audit Decisions":
    st.markdown("## 📊 Audit Hiring Decisions")
    example = json.dumps([
        {"candidate":"Alice Smith","gender":"female","decision":"rejected","reason":"not a culture fit"},
        {"candidate":"Bob Jones",  "gender":"male",  "decision":"approved","reason":"great culture fit"},
        {"candidate":"Maria Garcia","gender":"female","decision":"rejected","reason":"overqualified"},
        {"candidate":"James Lee",  "gender":"male",  "decision":"approved","reason":"strong skills"}
    ], indent=2)
    st.code(example, language="json")
    raw = st.text_area("Paste your decisions JSON here:", height=200)

    if st.button("📊 Run Audit"):
        if not raw.strip():
            st.warning("Paste your decisions JSON.")
        else:
            try: decisions = json.loads(raw)
            except: st.error("Invalid JSON format."); st.stop()
            with st.spinner("Running audit..."):
                try:
                    r = requests.post(f"{API_URL}/audit-decisions", json={"decisions": decisions})
                    result = r.json()
                    c1,c2,c3 = st.columns(3)
                    bias_det = result.get("systemic_bias_detected", False)
                    overall  = result.get("overall_risk","?").upper()
                    icons    = {"LOW":"🟢","MEDIUM":"🟡","HIGH":"🔴","CRITICAL":"🚨"}
                    with c1: st.metric("Systemic Bias", "🔴 YES" if bias_det else "🟢 NO")
                    with c2: st.metric("Overall Risk",  f"{icons.get(overall,'⚪')} {overall}")
                    with c3: st.metric("Audit Score",   f"{result.get('audit_score',0)}/100")

                    for p in result.get("patterns_found",[]):
                        sev = p.get("severity","low")
                        with st.expander(f"{'🔴' if sev=='high' else '🟡'} {p.get('pattern','')}"):
                            st.markdown(f"**Affected Group:** {p.get('affected_group','')}")
                            st.markdown(f"**Evidence:** {p.get('evidence','')}")

                    for f in result.get("decisions_flagged",[]): st.error(f"🚩 {f}")
                    for rec in result.get("recommendations",[]): st.info(f"💡 {rec}")
                    if result.get("requires_legal_review"):
                        st.error(f"⚖️ LEGAL REVIEW REQUIRED: {result.get('legal_review_reason','')}")
                except Exception as e:
                    st.error(f"API error: {e}")

# ── PAGE 6 — PDF REPORT ──────────────────────
elif page == "📄 Download PDF Report":
    st.markdown("## 📄 Download Executive PDF Report")
    st.markdown("This generates a **CEO-ready 4-page PDF** with all your analysis, scores, bias flags and recommendations.")
    st.markdown("---")

    st.info("💡 The more modules you run before downloading, the richer the report will be.")

    has_problem  = "problem_analysis" in st.session_state
    has_scoring  = "scoring_result"   in st.session_state
    has_bias     = "bias_result"      in st.session_state
    has_decision = "decision_result"  in st.session_state

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"{'✅' if has_problem  else '⬜'} Problem Analysis")
        st.markdown(f"{'✅' if has_scoring  else '⬜'} Candidate Scoring")
    with col2:
        st.markdown(f"{'✅' if has_bias     else '⬜'} Bias Detection")
        st.markdown(f"{'✅' if has_decision else '⬜'} Hiring Decision")

    st.markdown("---")

    if st.button("📄 Generate & Download PDF Report"):
        with st.spinner("Generating CEO-ready PDF..."):
            try:
                payload = {
                    "problem_text":     st.session_state.get("problem_text", ""),
                    "problem_analysis": st.session_state.get("problem_analysis"),
                    "candidates":       st.session_state.get("candidates"),
                    "scoring_result":   st.session_state.get("scoring_result"),
                    "bias_result":      st.session_state.get("bias_result"),
                    "decision_result":  st.session_state.get("decision_result"),
                }
                r = requests.post(f"{API_URL}/generate-report", json=payload)
                if r.status_code == 200 and r.headers.get("content-type") == "application/pdf":
                    st.download_button(
                        label="⬇️ Click Here to Download PDF",
                        data=r.content,
                        file_name="hr_decision_report.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF ready! Click the button above to download.")
                else:
                    st.error(f"PDF generation failed: {r.text}")
            except Exception as e:
                st.error(f"API error: {e}")
