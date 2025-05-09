from app.web.app import create_web_app
from waitress import serve
from config.settings import WEB_APP_PORT

if __name__ == "__main__":
    app = create_web_app()
    serve(app, host="0.0.0.0", port=WEB_APP_PORT)
