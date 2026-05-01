from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import re
import hashlib
import time

from services.shared import groq_client as client
from services.shared import cache_client as cache
from services.shared import chroma_client

describe_bp = Blueprint("describe", __name__)


# 🔹 Load prompt once (better performance)
def load_prompt():
    with open("prompts/describe_prompt.txt", "r") as f:
        return f.read()


PROMPT_TEMPLATE = load_prompt()


# 🔹 Cache key generator (better than raw text)
def generate_cache_key(text):
    return hashlib.sha256(text.encode()).hexdigest()


@describe_bp.route("/describe", methods=["POST"])
def describe():
    """
    Analyze fraud risk using AI + RAG context
    ---
    tags:
      - Describe
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              example: User transferred 50000 to unknown offshore account
    responses:
      200:
        description: Fraud risk analysis result
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                risk_level:
                  type: string
                  example: High
                explanation:
                  type: string
                key_indicators:
                  type: array
                  items:
                    type: string
            meta:
              type: object
              properties:
                model_used:
                  type: string
                  example: llama-3.3-70b-versatile
                response_time_ms:
                  type: integer
                cached:
                  type: boolean
    """
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]

        # 🔹 Cache lookup
        key = generate_cache_key(text)
        cached = cache.get(key)

        if cached:
            return jsonify(json.loads(cached))

        # 🔹 RAG Context
        context_docs = chroma_client.query(text)
        context = "\n".join(context_docs[0]) if context_docs else ""

        # 🔹 Final prompt
        prompt = f"""
Context:
{context}

{PROMPT_TEMPLATE.replace("{text}", text)}
"""

        # 🔹 Call LLM
        start = time.time()
        response = client.generate(prompt, temperature=0.1)
        end = time.time()

        # 🔹 Safe JSON parsing
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)

            if json_match:
                parsed = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")

        except Exception:
            parsed = {
                "risk_level": "Unknown",
                "explanation": "Model returned invalid format",
                "key_indicators": []
            }

        # 🔹 Final structured response
        result = {
            "data": parsed,
            "meta": {
                "model_used": client.model,
                "response_time_ms": int((end - start) * 1000),
                "cached": False
            }
        }

        # 🔹 Store in cache
        try:
            cache.set(key, json.dumps(result))
        except Exception:
            pass  # cache failure shouldn't break API

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500