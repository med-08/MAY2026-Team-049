import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import db

from auth import auth_bp
from parent import parent_bp
from admin import admin_bp
from student import student_bp
from tutor import tutor_bp


def ensure_database_compatibility(db_path):
    """Apply only safe, additive compatibility fixes to an existing SQLite DB.

    The project model contains AssignmentSubmission.progress_percentage, while
    older copies of learnathome.db may not have that column.  Adding the
    nullable/defaulted column preserves all existing rows and lets SQLAlchemy
    query the model normally. No tables or existing data are removed.
    """
    connection = sqlite3.connect(db_path)
    try:
        columns = {row[1] for row in connection.execute(
            "PRAGMA table_info(assignment_submission)"
        ).fetchall()}
        if columns and "progress_percentage" not in columns:
            connection.execute(
                "ALTER TABLE assignment_submission "
                "ADD COLUMN progress_percentage INTEGER DEFAULT 0"
            )

        # Add the Google Meet URL to existing Session tables without
        # dropping/recreating anything. Existing sessions remain intact.
        session_columns = {row[1] for row in connection.execute(
            "PRAGMA table_info(session)"
        ).fetchall()}
        if session_columns and "meeting_url" not in session_columns:
            connection.execute(
                "ALTER TABLE session ADD COLUMN meeting_url VARCHAR(500)"
            )

        connection.commit()
    finally:
        connection.close()


def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'learnathome.db')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'
    # Keep API exceptions as JSON responses so browser clients receive CORS
    # headers instead of the Werkzeug HTML debugger page.
    app.config['PROPAGATE_EXCEPTIONS'] = False

    db.init_app(app)

    # Keep the existing real database intact while applying only the
    # additive compatibility fix needed by the current SQLAlchemy models.
    ensure_database_compatibility(DB_PATH)

    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ], "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]}}
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

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        # Roll back any failed SQLAlchemy transaction before the next request.
        try:
            db.session.rollback()
        except Exception:
            pass
        app.logger.exception("Unhandled API exception: %s", e)
        return jsonify({
            "success": False,
            "message": "Internal Server Error (500)",
            # Safe diagnostic text makes frontend/API debugging possible
            # without returning the interactive Werkzeug debugger page.
            "error": str(e)
        }), 500

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
    debug = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes')
    app.run(debug=debug, host='127.0.0.1', port=5000)