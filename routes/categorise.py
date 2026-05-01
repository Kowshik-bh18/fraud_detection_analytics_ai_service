from flask import Blueprint, request, jsonify
import json
import re
import time
import hashlib

from services.shared import groq_client as client
from services.shared import cache_client as cache

categorise_bp = Blueprint("categorise", __name__)


def load_prompt():
    with open("prompts/categorise_prompt.txt", "r") as file:
        return file.read()


# ✅ Normalize input to avoid cache misses
def generate_cache_key(text):
    normalized = text.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


@categorise_bp.route("/categorise", methods=["POST"])
def categorise():
    """
    Categorize input text into fraud-related category
    ---
    tags:
      - Categorise
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              example: User transferred large amount to unknown account
    responses:
      200:
        description: Categorization result
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                category:
                  type: string
                confidence:
                  type: number
                reasoning:
                  type: string
            meta:
              type: object
              properties:
                confidence:
                  type: number
                model_used:
                  type: string
                tokens_used:
                  type: integer
                response_time_ms:
                  type: integer
                cached:
                  type: boolean
    """
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        input_text = data["text"]
        key = generate_cache_key(input_text)

        # 🔥 Step 1: Check cache
        cached = cache.get(key)

        if cached:
            # handle Redis bytes safely
            cached_data = json.loads(
                cached.decode() if isinstance(cached, bytes) else cached
            )
            cached_data["meta"]["cached"] = True
            return jsonify(cached_data), 200

        # 🔥 Step 2: Generate prompt
        prompt_template = load_prompt()
        prompt = prompt_template.format(input_text=input_text)

        # 🔥 Step 3: Call LLM
        start = time.time()
        response = client.generate(prompt)
        end = time.time()

        # 🔥 Step 4: Extract JSON safely
        try:
            json_match = re.search(r'\{[\s\S]*?\}', response)

            if json_match:
                parsed_response = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")

        except Exception:
            parsed_response = {
                "category": "Other",
                "confidence": 0.0,
                "reasoning": response
            }

        # 🔥 Step 5: Final response
        result = {
            "data": parsed_response,
            "meta": {
                "confidence": parsed_response.get("confidence", 0.0),
                "model_used": client.model,
                "tokens_used": len(prompt.split()),
                "response_time_ms": int((end - start) * 1000),
                "cached": False
            }
        }

        # 🔥 Step 6: Store in cache
        cache.set(key, json.dumps(result))  # add TTL here if needed

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500