import os
from flask import Flask, jsonify
from flask_cors import CORS
from database import db

from auth import auth_bp
from parent import parent_bp
from admin import admin_bp
from student import student_bp
from tutor import tutor_bp


def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'learnathome.db')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'

    db.init_app(app)

    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ]}}
    )

    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            "success": True,
            "message": "LearnAtHome backend is running.",
            "database_path": DB_PATH
        }), 200

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            "success": True,
            "message": "Server healthy",
            "database_path": DB_PATH
        }), 200

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(parent_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(tutor_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "message": "Resource Not Found (404)"
        }), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "success": False,
            "message": "Internal Server Error (500)"
        }), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)