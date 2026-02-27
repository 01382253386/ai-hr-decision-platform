# ⚡ AI HR Decision Platform

> **AI-powered hiring decisions with built-in bias detection, candidate scoring, and CEO-ready PDF reports.**  
> Built in 6 days using Python, FastAPI, Claude AI (Anthropic), and Streamlit.

---

## 🎯 What It Does

Most companies are adopting AI in hiring faster than they are auditing it for fairness.

**67% of companies now use AI in hiring. Only 26% of candidates trust it.**

This platform bridges that gap — it makes AI hiring decisions faster AND documents them for bias, compliance, and audit purposes.

### Five Modules:

| Module | What It Does |
|--------|-------------|
| 🔍 **Analyse Problem** | Paste any HR problem in plain English → AI extracts urgency, constraints, hidden risks |
| 👥 **Score Candidates** | Role-based weighted scoring (technical / executive / operational) with confidence bands |
| ✅ **Create Decision** | AI-powered APPROVE / REJECT with reasoning and next step recommendation |
| 🚨 **Detect Bias** | Scans job descriptions and interview notes for 8 bias types with legal risk and suggested rewrites |
| 📄 **PDF Report** | One-click 4-page CEO-ready report with full audit trail |

---

## 🚨 Bias Detection — The Core Feature

Feed it a real job description:

> *"We need a young energetic rockstar developer who fits our culture. Recent CS grad from top university preferred."*

**Result in 3 seconds:**

- 🔴 **Age Discrimination (HIGH)** — trigger: "young" — violates ADEA
- 🟠 **Educational Elitism (MEDIUM)** — trigger: "top university" — creates disparate impact
- 🟠 **Culture Fit Vagueness (MEDIUM)** — known legal proxy for racial/gender discrimination

Each flag includes: exact trigger phrase, legal explanation, compliance risk, and suggested rewrite.

---

## 🏗️ Tech Stack

```
Backend:   Python 3.13 + FastAPI
AI Engine: Claude Haiku (Anthropic API)
Frontend:  Streamlit
PDF:       ReportLab
Server:    Uvicorn
```

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-hr-decision-platform.git
cd ai-hr-decision-platform
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn anthropic python-dotenv streamlit reportlab
```

### 3. Add your API key

Create a file called `.env` in the project folder:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Get your free API key at: `console.anthropic.com`

### 4. Start the backend (Terminal 1)

```bash
uvicorn main:app --reload
```

Wait for: `Application startup complete`

### 5. Start the frontend (Terminal 2)

```bash
streamlit run app.py
```

### 6. Open in browser

```
http://localhost:8501
```

---

## 📡 API Endpoints

All endpoints available at `http://localhost:8000/docs` (Swagger UI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server status check |
| POST | `/analyse-problem` | Extract structured data from HR problems |
| POST | `/score-candidates` | Role-weighted candidate ranking |
| POST | `/create-decision` | AI hiring decision with reasoning |
| POST | `/detect-bias` | Scan content for bias patterns |
| POST | `/audit-decisions` | Systemic bias analysis across decision batches |
| POST | `/bias-score-candidates` | Scoring with integrated bias check |
| POST | `/generate-report` | Generate CEO-ready PDF report |

---

## 📊 Why This Matters — Industry Context

- **67%** of companies now use AI in hiring (up from 26% in 2024)
- **Only 26%** of candidates trust AI to evaluate them fairly (Gartner 2026)
- **New York City** legally requires annual bias audits before using any AI hiring tool
- **California** extended anti-discrimination laws to cover AI hiring tools in 2025
- **EU AI Act** classifies hiring AI as high-risk — requiring documentation and human oversight

Your PDF audit trail is the documentation these laws require.

---

## 📁 Project Structure

```
ai-hr-decision-platform/
│
├── main.py          # FastAPI backend — all API endpoints
├── app.py           # Streamlit frontend — visual UI
├── report.py        # ReportLab PDF generator
├── .env             # Your API key (NOT uploaded to GitHub)
├── .gitignore       # Prevents .env from being uploaded
└── README.md        # This file
```

---

## 🔒 Security Note

Your `.env` file containing your Anthropic API key is excluded from this repository via `.gitignore`.  
Never commit API keys to GitHub. If you accidentally do, rotate your key immediately at `console.anthropic.com`.

---

## 🗺️ Roadmap

- [ ] User authentication and multi-tenancy
- [ ] PostgreSQL database for decision history
- [ ] Interview question generator
- [ ] Offer letter drafting module
- [ ] Knowledge layer — learns from company's own hiring history
- [ ] Workday / Greenhouse / Lever integrations
- [ ] SOC 2 compliance

---

## 👤 Author

Built by a system thinker exploring the intersection of AI, HR compliance, and enterprise decision-making.

Connect on LinkedIn: `your-linkedin-url`  
Follow on X: `your-x-handle`

---

## 📄 License

MIT License — free to use, modify, and build on.

---

*Built in 6 days. Under 500 lines of code. Powered by Claude AI.*
