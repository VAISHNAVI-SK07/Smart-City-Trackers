import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config
from routes.auth_routes import auth_bp
from routes.citizen_routes import citizen_bp
from routes.admin_routes import admin_bp
from routes.notification_routes import notification_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # supports_credentials=True is required so the browser will send the
    # session cookie along with requests from our frontend (a different
    # origin/port during local development).
    CORS(app, supports_credentials=True)

    # Make sure the uploads folder exists before any file is saved to it.
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Simple endpoint to confirm the server is up and reachable."""
        return {'status': 'ok', 'message': 'Smart Civic Tracker API is running.'}, 200

    @app.route('/uploads/<path:filename>', methods=['GET'])
    def uploaded_file(filename):
        """Serves uploaded complaint images so the frontend can display them."""
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)