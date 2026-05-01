from flask import Blueprint, jsonify
import time

from services.metrics import start_time
from services.shared import groq_client as groq
from services.shared import cache_client as cache
from services.shared import chroma_client as chroma

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """
    Health check and system metrics
    ---
    tags:
      - Health
    responses:
      200:
        description: System health and metrics
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            model:
              type: string
              example: llama-3.3-70b-versatile
            avg_response_time_ms:
              type: number
              example: 850.5
            chroma_doc_count:
              type: integer
              example: 120
            uptime_seconds:
              type: integer
              example: 3600
            cache:
              type: object
              example:
                hits: 10
                misses: 5
    """
    uptime = int(time.time() - start_time)

    return jsonify({
        "status": "healthy",
        "model": groq.model,
        "avg_response_time_ms": round(groq.get_avg_response_time(), 2),
        "chroma_doc_count": chroma.collection.count(),
        "uptime_seconds": uptime,
        "cache": cache.get_stats()
    })