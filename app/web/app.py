from flask import Flask, send_from_directory
from flask_cors import CORS
from app.web.routes import register_routes

def create_web_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    CORS(app)  # Enable CORS for all routes
    register_routes(app)

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    return app