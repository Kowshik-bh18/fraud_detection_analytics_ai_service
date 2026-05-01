from flask import Blueprint, request, jsonify
import hashlib
import json
import time

from services.shared import groq_client as groq
from services.shared import cache_client as cache
from services.shared import chroma_client as chroma

query_bp = Blueprint("query", __name__)


def load_prompt():
    with open("prompts/query_prompt.txt", "r") as f:
        return f.read()


def generate_cache_key(question):
    return hashlib.sha256(question.encode()).hexdigest()


@query_bp.route("/query", methods=["POST"])
def query():
    """
    Ask a question using RAG (Retrieval-Augmented Generation)
    ---
    tags:
      - Query
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            question:
              type: string
              example: What are common fraud patterns in banking transactions?
    responses:
      200:
        description: Answer generated using AI with supporting context
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                answer:
                  type: string
                sources:
                  type: array
                  items:
                    type: string
            meta:
              type: object
              properties:
                confidence:
                  type: number
                  example: 0.66
                model_used:
                  type: string
                  example: llama-3.3-70b-versatile
                tokens_used:
                  type: integer
                response_time_ms:
                  type: integer
                cached:
                  type: boolean
    """
    try:
        data = request.get_json()

        if not data or "question" not in data:
            return jsonify({"error": "Missing 'question'"}), 400

        question = data["question"]

        key = generate_cache_key(question)

        # 🔥 Check cache
        cached = cache.get(key)
        if cached:
            cached_data = json.loads(cached)
            cached_data["meta"]["cached"] = True
            return jsonify(cached_data)

        # 🔥 RAG pipeline
        docs = chroma.query(question)
        sources = docs[0] if docs else []

        context = "\n".join([f"- {doc}" for doc in sources])

        prompt_template = load_prompt()
        prompt = prompt_template.format(context=context, question=question)

        # 🔥 Timing
        start = time.time()
        answer = groq.generate(prompt)
        end = time.time()

        response_time = int((end - start) * 1000)

        response = {
            "data": {
                "answer": answer,
                "sources": sources
            },
            "meta": {
                "confidence": round(len(sources) / 3, 2),
                "model_used": groq.model,
                "tokens_used": len(prompt.split()),
                "response_time_ms": response_time,
                "cached": False
            }
        }

        # 🔥 Store in cache
        cache.set(key, json.dumps(response))

        return jsonify(response)

    except Exception:
        return jsonify({"error": "Internal server error"}), 500