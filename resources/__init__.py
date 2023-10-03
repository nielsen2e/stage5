from flask import Flask, jsonify
from resources.config import Config
from dotenv import load_dotenv
from flask_smorest import Api
from resources.views import blp as VideoBlueprint


def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config.from_object(Config)
    api = Api(app)

    @app.route("/")
    def hello():
        return jsonify({"greeting": "Hello World"})

    api.register_blueprint(VideoBlueprint)

    return app
