from flask import Blueprint, request, jsonify
import json
import re
import time

from services.shared import groq_client as client

analyse_bp = Blueprint("analyse", __name__)


def load_prompt():
    with open("prompts/analyse_prompt.txt") as f:
        return f.read()


PROMPT = load_prompt()


@analyse_bp.route("/analyse", methods=["POST"])
def analyse():
    """
    Analyze document for fraud risks
    ---
    tags:
      - Analyse
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              example: Invoice with suspicious entries and mismatched totals
    responses:
      200:
        description: Analysis result
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                summary:
                  type: string
                risks:
                  type: array
                  items:
                    type: string
                key_findings:
                  type: array
                  items:
                    type: string
            meta:
              type: object
              properties:
                model_used:
                  type: string
                response_time_ms:
                  type: integer
    """
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]

        prompt = PROMPT.replace("{text}", text)

        start = time.time()
        response = client.generate(prompt, temperature=0.2)
        end = time.time()

        try:
            json_match = re.search(r'\{[\s\S]*\}', response)

            if json_match:
                parsed = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")

        except:
            parsed = {
                "summary": "Unable to analyse",
                "risks": [],
                "key_findings": []
            }

        return jsonify({
            "data": parsed,
            "meta": {
                "model_used": client.model,
                "response_time_ms": int((end - start) * 1000)
            }
        })

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500