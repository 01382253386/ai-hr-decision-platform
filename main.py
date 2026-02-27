from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import anthropic
import os
import json
from dotenv import load_dotenv
from report import generate_report

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI(title="AI HR Decision Platform")

WEIGHTS = {
    "technical":   {"skill_match": 0.35, "culture_fit": 0.15, "execution_speed": 0.20, "cost_efficiency": 0.15, "adaptability": 0.15},
    "executive":   {"skill_match": 0.20, "culture_fit": 0.30, "execution_speed": 0.15, "cost_efficiency": 0.15, "adaptability": 0.20},
    "operational": {"skill_match": 0.30, "culture_fit": 0.20, "execution_speed": 0.25, "cost_efficiency": 0.15, "adaptability": 0.10}
}

class DecisionRequest(BaseModel):
    candidate_name: str
    position: str
    experience_years: int
    skills: list[str]
    notes: Optional[str] = None

class ProblemRequest(BaseModel):
    problem: str

class ScoringRequest(BaseModel):
    candidates: list[dict]
    role_type: str = "technical"

class BiasRequest(BaseModel):
    job_description: Optional[str] = None
    interview_notes: Optional[str] = None
    decision_reasoning: Optional[str] = None

class BiasAuditRequest(BaseModel):
    decisions: list[dict]

class PDFReportRequest(BaseModel):
    problem_text: Optional[str] = None
    problem_analysis: Optional[dict] = None
    candidates: Optional[list[dict]] = None
    scoring_result: Optional[dict] = None
    bias_result: Optional[dict] = None
    decision_result: Optional[dict] = None

@app.get("/")
def root():
    return {"message": "AI HR Decision Platform is running", "status": "active"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "5.0.0"}

@app.post("/analyse-problem")
def analyse_problem(request: ProblemRequest):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""Respond with raw JSON only. No markdown. No backticks. No code blocks.

You are an HR decision analyst. Extract structured data from the input.
Return ONLY this JSON structure:
{{
  "urgency": "low" or "medium" or "high",
  "business_need": "one sentence summary",
  "problem_type": "hiring" or "retention" or "performance" or "restructure",
  "constraints": ["list of constraints"],
  "success_goals": ["list of goals"],
  "hidden_risks": ["list of risks NOT mentioned but inferred"]
}}

Input: {request.problem}"""
        }]
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    try:
        return json.loads(text)
    except:
        return {"error": "Could not parse response", "raw": text}

@app.post("/score-candidates")
def score_candidates(request: ScoringRequest):
    weights = WEIGHTS.get(request.role_type, WEIGHTS["technical"])
    scored = []
    for candidate in request.candidates:
        name = candidate.get("name", "Unknown")
        scores = {
            "skill_match":      candidate.get("skill_match", 3),
            "culture_fit":      candidate.get("culture_fit", 3),
            "execution_speed":  candidate.get("execution_speed", 3),
            "cost_efficiency":  candidate.get("cost_efficiency", 3),
            "adaptability":     candidate.get("adaptability", 3)
        }
        filled = sum(1 for v in scores.values() if v != 3)
        total  = round(sum(scores[k] * weights[k] * 20 for k in scores))
        margin = round((1 - filled/5) * 15)
        scored.append({
            "name": name, "score": total,
            "confidence": f"± {margin}",
            "top_strength": max(scores, key=scores.get),
            "top_risk":     min(scores, key=scores.get),
            "role_type": request.role_type
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"ranking": scored, "weights_used": weights, "role_type": request.role_type}

@app.post("/create-decision")
def create_decision(request: DecisionRequest):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""You are an expert HR decision maker.
Evaluate this candidate and give a hiring decision.

Candidate: {request.candidate_name}
Position: {request.position}
Experience: {request.experience_years} years
Skills: {", ".join(request.skills)}
Notes: {request.notes}

Respond in this exact format:
DECISION: APPROVE or REJECT
CONFIDENCE: a number between 0 and 1
REASONING: one sentence explanation
RECOMMENDATION: one action to take next"""
        }]
    )
    text = message.content[0].text
    result = {}
    for line in text.strip().split("\n"):
        if "DECISION:"         in line: result["decision"]       = line.split("DECISION:")[1].strip()
        elif "CONFIDENCE:"     in line: result["confidence"]     = line.split("CONFIDENCE:")[1].strip()
        elif "REASONING:"      in line: result["reasoning"]      = line.split("REASONING:")[1].strip()
        elif "RECOMMENDATION:" in line: result["recommendation"] = line.split("RECOMMENDATION:")[1].strip()
    return {"candidate": request.candidate_name, "position": request.position, **result}

@app.post("/detect-bias")
def detect_bias(request: BiasRequest):
    content = ""
    if request.job_description:    content += f"\n[JOB DESCRIPTION]\n{request.job_description}"
    if request.interview_notes:    content += f"\n[INTERVIEW NOTES]\n{request.interview_notes}"
    if request.decision_reasoning: content += f"\n[DECISION REASONING]\n{request.decision_reasoning}"
    if not content.strip():
        return {"error": "No content provided."}
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[{
            "role": "user",
            "content": f"""Respond with raw JSON only. No markdown. No backticks. No code blocks.

You are an HR bias detection expert. Analyse the content below for bias.

Return ONLY this JSON:
{{
  "overall_bias_risk": "low" or "medium" or "high" or "critical",
  "bias_score": a number from 0 to 100,
  "flags": [
    {{
      "type": "bias type name",
      "severity": "low" or "medium" or "high",
      "trigger_text": "the exact phrase that triggered this flag",
      "explanation": "why this is biased",
      "suggested_fix": "how to rewrite it"
    }}
  ],
  "clean_summary": "one paragraph rewrite with bias removed",
  "compliance_risk": "low" or "medium" or "high",
  "compliance_note": "one sentence on legal exposure"
}}

CONTENT TO ANALYSE:
{content}"""
        }]
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    try:
        return json.loads(text)
    except:
        return {"error": "Could not parse response", "raw": text}

@app.post("/audit-decisions")
def audit_decisions(request: BiasAuditRequest):
    if not request.decisions:
        return {"error": "No decisions provided."}
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[{
            "role": "user",
            "content": f"""Respond with raw JSON only. No markdown. No backticks. No code blocks.

You are an HR audit specialist. Analyse this batch of hiring decisions for systemic bias patterns.

Return ONLY this JSON:
{{
  "systemic_bias_detected": true or false,
  "overall_risk": "low" or "medium" or "high" or "critical",
  "audit_score": a number from 0 to 100,
  "patterns_found": [
    {{
      "pattern": "description of the bias pattern",
      "affected_group": "which group is disadvantaged",
      "evidence": "which decisions show this pattern",
      "severity": "low" or "medium" or "high"
    }}
  ],
  "decisions_flagged": ["list of candidate names that seem unfairly treated"],
  "recommendations": ["list of process changes to reduce bias"],
  "requires_legal_review": true or false,
  "legal_review_reason": "why legal review is needed or null"
}}

DECISIONS TO AUDIT:
{json.dumps(request.decisions, indent=2)}"""
        }]
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    try:
        return json.loads(text)
    except:
        return {"error": "Could not parse response", "raw": text}

@app.post("/bias-score-candidates")
def bias_score_candidates(request: ScoringRequest):
    weights = WEIGHTS.get(request.role_type, WEIGHTS["technical"])
    scored = []
    for candidate in request.candidates:
        name = candidate.get("name", "Unknown")
        scores = {
            "skill_match":      candidate.get("skill_match", 3),
            "culture_fit":      candidate.get("culture_fit", 3),
            "execution_speed":  candidate.get("execution_speed", 3),
            "cost_efficiency":  candidate.get("cost_efficiency", 3),
            "adaptability":     candidate.get("adaptability", 3)
        }
        filled = sum(1 for v in scores.values() if v != 3)
        total  = round(sum(scores[k] * weights[k] * 20 for k in scores))
        margin = round((1 - filled/5) * 15)
        scored.append({
            "name": name, "score": total,
            "confidence": f"± {margin}",
            "top_strength": max(scores, key=scores.get),
            "top_risk":     min(scores, key=scores.get),
            "role_type": request.role_type,
            "raw_scores": scores
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""Respond with raw JSON only. No markdown. No backticks. No code blocks.

You are a bias auditor. Review these candidate scores for scoring bias patterns.

Return ONLY this JSON:
{{
  "scoring_bias_risk": "low" or "medium" or "high",
  "bias_warnings": ["list of specific warnings about the scores"],
  "suspicious_candidates": ["names of candidates whose scores look suspicious"],
  "recommendation": "one sentence on whether to trust this scoring or re-evaluate"
}}

SCORES:
{json.dumps(scored, indent=2)}"""
        }]
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    try:
        bias_check = json.loads(text)
    except:
        bias_check = {"error": "Could not parse bias check", "raw": text}
    return {
        "ranking": scored, "weights_used": weights,
        "role_type": request.role_type, "bias_audit": bias_check
    }

# ─────────────────────────────────────────────
# DAY 6 — PDF REPORT
# ─────────────────────────────────────────────

@app.post("/generate-report")
def generate_pdf_report(request: PDFReportRequest):
    try:
        pdf_bytes = generate_report(
            problem_text=request.problem_text or "",
            problem_analysis=request.problem_analysis,
            candidates=request.candidates,
            scoring_result=request.scoring_result,
            bias_result=request.bias_result,
            decision_result=request.decision_result
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=hr_decision_report.pdf"}
        )
    except Exception as e:
        return {"error": str(e)}
