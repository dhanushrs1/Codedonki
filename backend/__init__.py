"""
CodeDonki Flask Application Factory
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates')
    )

    # --- Config ---
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "changeme-jwt-secret")
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "changeme-flask-secret")
    app.config["UPLOAD_FOLDER"] = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads'
    )

    # --- CORS ---
    # Allow all origins with credentials=False (JWT in Authorization header, not cookies)
    CORS(app, origins="*", supports_credentials=False)

    # --- Register Blueprints ---
    from backend.routes.auth import auth_bp
    from backend.routes.lessons import lessons_bp
    from backend.routes.admin import admin_bp
    from backend.routes.quiz import quiz_bp
    from backend.routes.badges import badges_bp
    from backend.routes.users import users_bp
    from backend.routes.ai import ai_bp
    from backend.routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(lessons_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(badges_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(pages_bp)

    # Serve uploaded files
    from flask import send_from_directory
    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app
