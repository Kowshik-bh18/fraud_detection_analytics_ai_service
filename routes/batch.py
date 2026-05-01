from flask import Blueprint, request, jsonify
import time, json, re

from services.shared import groq_client as client

batch_bp = Blueprint("batch", __name__)


def load_prompt():
    with open("prompts/describe_prompt.txt") as f:
        return f.read()


PROMPT = load_prompt()


@batch_bp.route("/batch", methods=["POST"])
def batch():
    """
    Batch fraud risk analysis
    ---
    tags:
      - Batch
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: string
              example:
                - Fraud transaction
                - Unauthorized login attempt
    responses:
      200:
        description: Batch analysis results
        schema:
          type: object
          properties:
            results:
              type: array
              items:
                type: object
                properties:
                  input:
                    type: string
                  output:
                    type: object
                    properties:
                      risk_level:
                        type: string
                      explanation:
                        type: string
                      key_indicators:
                        type: array
                        items:
                          type: string
                  meta:
                    type: object
                    properties:
                      response_time_ms:
                        type: integer
            meta:
              type: object
              properties:
                total_items:
                  type: integer
                total_time_ms:
                  type: integer
                model_used:
                  type: string
    """

    try:
        data = request.get_json()

        if not data or "items" not in data:
            return jsonify({"error": "Missing 'items' field"}), 400

        items = data["items"]

        start_time = time.time()

        results = []

        for item in items:
            item_start = time.time()

            try:
                # 🔹 Prompt
                prompt = PROMPT.replace("{text}", item)

                response = client.generate(prompt, temperature=0.1)

                # 🔹 Safe JSON parsing
                json_match = re.search(r'\{[\s\S]*\}', response)

                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = {
                        "risk_level": "Unknown",
                        "explanation": "Invalid response",
                        "key_indicators": []
                    }

            except Exception:
                parsed = {
                    "risk_level": "Error",
                    "explanation": "Processing failed",
                    "key_indicators": []
                }

            item_end = time.time()

            results.append({
                "input": item,
                "output": parsed,
                "meta": {
                    "response_time_ms": int((item_end - item_start) * 1000)
                }
            })

        end_time = time.time()

        return jsonify({
            "results": results,
            "meta": {
                "total_items": len(results),
                "total_time_ms": int((end_time - start_time) * 1000),
                "model_used": client.model
            }
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500