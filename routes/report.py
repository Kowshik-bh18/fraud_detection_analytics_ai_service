from flask import Blueprint, request, jsonify
from services.job_service import create_job, update_job, get_job, run_async
from services.shared import groq_client as groq
import requests
import json
import re

report_bp = Blueprint("report", __name__)


# ✅ Clean LLM JSON output
def extract_json(response):
    try:
        response = re.sub(r"```json|```", "", response).strip()

        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())

    except Exception:
        pass

    return None


# ✅ Core logic
def generate_report_logic(text):
    prompt = f"""
You are a fraud analysis expert.

Analyze the following text and generate a structured fraud report.

STRICT RULES:
- Return ONLY valid JSON
- No markdown, no ```json
- No nested objects
- Keep everything simple and clean

FORMAT:
{{
  "title": "...",
  "executive_summary": "...",
  "overview": "...",
  "top_items": ["item1", "item2"],
  "recommendations": ["rec1", "rec2"]
}}

Text:
{text}
"""

    response = groq.generate(prompt)

    parsed = extract_json(response)

    if parsed:
        return parsed

    # fallback
    return {
        "title": "Fraud Analysis Report",
        "executive_summary": "Suspicious activity detected",
        "overview": response,
        "top_items": ["Suspicious activity"],
        "recommendations": ["Investigate further"]
    }


# ✅ Background job
def process_job(job_id, text, webhook_url=None):
    try:
        result = generate_report_logic(text)

        update_job(job_id, {
            "status": "completed",
            "result": result
        })

        # 🔥 WEBHOOK SUPPORT
        if webhook_url:
            try:
                requests.post(
                    webhook_url,
                    json={
                        "job_id": job_id,
                        "status": "completed",
                        "result": result
                    },
                    timeout=5   # ✅ important fix
                )
            except Exception as e:
                print("⚠️ Webhook failed:", e)

    except Exception as e:
        update_job(job_id, {
            "status": "failed",
            "error": str(e)
        })


# ✅ Create job
@report_bp.route("/generate-report", methods=["POST"])
def generate_report():
    """
    Generate fraud report asynchronously (background job)
    ---
    tags:
      - Report
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              example: Suspicious transaction detected in account
            webhook_url:
              type: string
              example: https://your-app.onrender.com/webhook
    responses:
      200:
        description: Job created successfully
        examples:
          application/json:
            job_id: "abc123"
            status: "processing"
    """
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "text field is required"}), 400

    text = data["text"]
    webhook_url = data.get("webhook_url")

    job_id = create_job()

    run_async(process_job, (job_id, text, webhook_url))

    return jsonify({
        "job_id": job_id,
        "status": "processing"
    })


# ✅ Check job status
@report_bp.route("/job-status/<job_id>", methods=["GET"])
def job_status(job_id):
    """
    Get status of report generation job
    ---
    tags:
      - Report
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        example: abc123
    responses:
      200:
        description: Job status
        examples:
          application/json:
            status: "completed"
            result:
              title: "Fraud Analysis Report"
              executive_summary: "..."
              overview: "..."
              top_items: ["item1", "item2"]
              recommendations: ["rec1", "rec2"]
    """
    job = get_job(job_id)

    if not job:
        return jsonify({"error": "Invalid job_id"}), 404

    return jsonify(job)