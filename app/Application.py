import os
from api.Api import api_po
from flask import Flask
from flask_cors import CORS


class Application:

    @staticmethod
    def run() -> None:
        research: Flask = Flask(__name__)
        research.config["CORS-HEADERS"] = "Content-Type"
        CORS(research, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})

        research.register_blueprint(api_po)

        port = int(os.environ.get("PORT", 5000))

        research.run(host="0.0.0.0", port=port)
