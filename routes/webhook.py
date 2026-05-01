from flask import Blueprint, request, jsonify

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Webhook receiver endpoint for async job results
    ---
    tags:
      - Webhook
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            job_id:
              type: string
              example: abc123
            status:
              type: string
              example: completed
            result:
              type: object
              properties:
                title:
                  type: string
                executive_summary:
                  type: string
                overview:
                  type: string
                top_items:
                  type: array
                  items:
                    type: string
                recommendations:
                  type: array
                  items:
                    type: string
    responses:
      200:
        description: Webhook received successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: received
    """
    data = request.get_json()

    print("🔥 WEBHOOK RECEIVED:")
    print(data)

    return jsonify({
        "status": "received"
    }), 200