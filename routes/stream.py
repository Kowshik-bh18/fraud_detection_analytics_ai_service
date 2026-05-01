from flask import Blueprint, request, Response, stream_with_context
import time

from services.shared import groq_client as client

stream_bp = Blueprint("stream", __name__)


def load_prompt():
    with open("prompts/report_stream_prompt.txt") as f:
        return f.read()


PROMPT = load_prompt()


@stream_bp.route("/report-stream", methods=["GET"])
def report_stream():
    """
    Stream AI-generated fraud report using Server-Sent Events (SSE)
    ---
    tags:
      - Stream
    parameters:
      - name: text
        in: query
        type: string
        required: true
        example: fraud case involving suspicious transactions
    responses:
      200:
        description: Streaming response (SSE)
        content:
          text/event-stream:
            schema:
              type: string
              example: |
                event: start
                data: Stream started

                event: chunk
                data: Title: Fraudulent Activity Analysis

                event: chunk
                data: Executive Summary: ...

                event: meta
                data: {"model":"llama-3.3-70b-versatile","response_time_ms":850}

                event: done
                data: [DONE]
    """
    text = request.args.get("text")

    if not text:
        return {"error": "Missing 'text' query param"}, 400

    def generate():
        start_time = time.time()

        try:
            # 🔹 Build prompt
            prompt = PROMPT.replace("{text}", text)

            # 🔹 Get AI response
            output = client.generate(prompt)

            # 🔹 Send start event
            yield "event: start\ndata: Stream started\n\n"

            # 🔹 Stream line by line
            for line in output.split("\n"):
                yield f"event: chunk\ndata: {line}\n\n"
                time.sleep(0.05)  # smooth streaming

            # 🔹 End time
            end_time = time.time()

            # 🔹 Send metadata
            yield f"""event: meta
data: {{
  "model": "{client.model}",
  "response_time_ms": {int((end_time - start_time) * 1000)}
}}
\n\n"""

            # 🔹 Done event
            yield "event: done\ndata: [DONE]\n\n"

        except Exception as e:
            yield f"""event: error
data: {{
  "message": "{str(e)}"
}}
\n\n"""

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )