from flask import Blueprint, request, jsonify
import json, re, time

from services.shared import groq_client as client

recommend_bp = Blueprint("recommend", __name__)


def load_prompt():
    with open("prompts/recommend_prompt.txt") as f:
        return f.read()


PROMPT = load_prompt()


@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    """
    Generate fraud prevention recommendations using AI
    ---
    tags:
      - Recommend
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              example: User transferred large amount to unknown offshore account
    responses:
      200:
        description: AI-generated recommendations
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  action_type:
                    type: string
                    example: BLOCK_TRANSACTION
                  description:
                    type: string
                  priority:
                    type: string
                    example: HIGH
            meta:
              type: object
              properties:
                model_used:
                  type: string
                  example: llama-3.3-70b-versatile
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

        # 🔹 Safe JSON parsing
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)

            if json_match:
                parsed = json.loads(json_match.group())
            else:
                raise ValueError("No JSON array found")

        except:
            parsed = [
                {
                    "action_type": "MONITOR_ACCOUNT",
                    "description": "Fallback recommendation",
                    "priority": "LOW"
                }
            ]

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