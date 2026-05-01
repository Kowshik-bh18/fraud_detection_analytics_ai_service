from flask import Flask
from flasgger import Swagger
from routes.categorise import categorise_bp
from routes.query import query_bp
from routes.health import health_bp
from routes.report import report_bp
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.stream import stream_bp
from routes.analyse import analyse_bp
from routes.batch import batch_bp
from routes.webhook import webhook_bp




app = Flask(__name__)


from services.data_loader import load_data_to_chroma

app = Flask(__name__)

# Load dataset
load_data_to_chroma()

app.register_blueprint(categorise_bp)
app.register_blueprint(query_bp)
app.register_blueprint(health_bp)
app.register_blueprint(report_bp)
app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(stream_bp)
app.register_blueprint(analyse_bp)
app.register_blueprint(batch_bp)
app.register_blueprint(webhook_bp)


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger_template = {
    "info": {
        "title": "Fraud Detection AI API",
        "description": "AI-powered fraud analysis service (Groq + RAG + Streaming)",
        "version": "1.0.0"
    }
}

Swagger(app, config=swagger_config, template=swagger_template)

if __name__ == "__main__":
    app.run(debug=True)