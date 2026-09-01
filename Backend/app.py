import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import db
from werkzeug.security import generate_password_hash
from models import Role, Subject, Admin

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

        resource_columns = {row[1] for row in connection.execute("PRAGMA table_info(study_resource)").fetchall()}
        if resource_columns and "created_at" not in resource_columns:
            connection.execute("ALTER TABLE study_resource ADD COLUMN created_at DATETIME")
            connection.execute("UPDATE study_resource SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

        session_columns = {row[1] for row in connection.execute("PRAGMA table_info(session)").fetchall()}
        if session_columns:
            for column, definition in [("meeting_started_at", "DATETIME"), ("meeting_ended_at", "DATETIME"), ("meeting_duration_seconds", "INTEGER")]:
                if column not in session_columns:
                    connection.execute(f"ALTER TABLE session ADD COLUMN {column} {definition}")

        progress_columns = {row[1] for row in connection.execute("PRAGMA table_info(learning_progress)").fetchall()}
        if progress_columns:
            for column, definition in [("joined_at", "DATETIME"), ("completed_at", "DATETIME"), ("duration_seconds", "INTEGER"), ("completion_source", "VARCHAR(20)")]:
                if column not in progress_columns:
                    connection.execute(f"ALTER TABLE learning_progress ADD COLUMN {column} {definition}")

        meeting_columns = {row[1] for row in connection.execute("PRAGMA table_info(meeting_request)").fetchall()}
        if meeting_columns and "creator_type" not in meeting_columns:
            connection.execute("ALTER TABLE meeting_request ADD COLUMN creator_type VARCHAR(20)")
            meeting_columns.add("creator_type")
        if meeting_columns and "meeting_type" not in meeting_columns:
            connection.execute("ALTER TABLE meeting_request ADD COLUMN meeting_type VARCHAR(30)")
            meeting_columns.add("meeting_type")
        if meeting_columns and "session_id" not in meeting_columns:
            connection.execute("ALTER TABLE meeting_request ADD COLUMN session_id INTEGER")
            meeting_columns.add("session_id")
        if meeting_columns and "denial_reason" not in meeting_columns:
            connection.execute("ALTER TABLE meeting_request ADD COLUMN denial_reason VARCHAR(500)")
            meeting_columns.add("denial_reason")

        notification_columns = {row[1] for row in connection.execute("PRAGMA table_info(notification)").fetchall()}
        if notification_columns and "action_url" not in notification_columns:
            connection.execute("ALTER TABLE notification ADD COLUMN action_url VARCHAR(255)")

        quiz_question_columns = {row[1] for row in connection.execute("PRAGMA table_info(quiz_question)").fetchall()}
        if quiz_question_columns and "explanation" not in quiz_question_columns:
            connection.execute("ALTER TABLE quiz_question ADD COLUMN explanation TEXT")

        quiz_columns = {row[1] for row in connection.execute("PRAGMA table_info(quiz)").fetchall()}
        if quiz_columns:
            for column, definition in [
                ("assigned_student_id", "INTEGER"),
                ("topic", "VARCHAR(100)"),
                ("difficulty", "VARCHAR(20)"),
            ]:
                if column not in quiz_columns:
                    connection.execute(f"ALTER TABLE quiz ADD COLUMN {column} {definition}")

        quiz_attempt_columns = {row[1] for row in connection.execute("PRAGMA table_info(quiz_attempt)").fetchall()}
        if quiz_attempt_columns:
            for column, definition in [
                ("correct_count", "INTEGER"),
                ("total_questions", "INTEGER"),
                ("answers_json", "TEXT"),
                ("review_json", "TEXT"),
            ]:
                if column not in quiz_attempt_columns:
                    connection.execute(f"ALTER TABLE quiz_attempt ADD COLUMN {column} {definition}")

        # Students can now self-generate their own flashcard sets (no tutor
        # involved), so tutor_id must become optional. SQLite can't alter a
        # column's NOT NULL constraint directly, so rebuild the table only
        # if it still has the old constraint, preserving existing rows.
        flashcard_set_info = connection.execute("PRAGMA table_info(flashcard_set)").fetchall()
        tutor_id_col = next((c for c in flashcard_set_info if c[1] == "tutor_id"), None)
        if tutor_id_col and tutor_id_col[3] == 1:
            connection.execute("""
                CREATE TABLE flashcard_set_new (
                    set_id INTEGER PRIMARY KEY,
                    tutor_id INTEGER,
                    subject_id INTEGER NOT NULL,
                    assigned_student_id INTEGER,
                    title VARCHAR(100) NOT NULL,
                    topic VARCHAR(100),
                    class_level VARCHAR(50),
                    context TEXT,
                    created_at DATETIME
                )
            """)
            connection.execute("""
                INSERT INTO flashcard_set_new
                    (set_id, tutor_id, subject_id, assigned_student_id, title, topic, class_level, context, created_at)
                SELECT set_id, tutor_id, subject_id, assigned_student_id, title, topic, class_level, context, created_at
                FROM flashcard_set
            """)
            connection.execute("DROP TABLE flashcard_set")
            connection.execute("ALTER TABLE flashcard_set_new RENAME TO flashcard_set")

        connection.commit()
    finally:
        connection.close()


def initialize_core_data():
    """Create only the minimum real application data required for a fresh DB.

    This deliberately creates no sample students, parents, tutors, sessions,
    bookings, messages, or other mock activity. Existing rows are preserved.
    """
    roles = {}
    for role_name in ('Admin', 'Tutor', 'Parent', 'Student'):
        role = Role.query.filter_by(role_name=role_name).first()
        if not role:
            role = Role(role_name=role_name)
            db.session.add(role)
            db.session.flush()
        roles[role_name] = role

    subjects = ('English', 'Mathematics', 'Physics', 'Science', 'Chemistry', 'Biology')
    for subject_name in subjects:
        if not Subject.query.filter_by(subject_name=subject_name).first():
            db.session.add(Subject(subject_name=subject_name))

    # Create only the system administrator when a fresh DB has no admin.
    if not Admin.query.filter_by(username='admin').first():
        db.session.add(
            Admin(
                role_id=roles['Admin'].role_id,
                username='admin',
                password_hash=generate_password_hash('admin123'),
                admin_name='Admin User',
                email='admin@learnathome.com'
            )
        )

    db.session.commit()


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
    with app.app_context():
        db.create_all()
        initialize_core_data()

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
