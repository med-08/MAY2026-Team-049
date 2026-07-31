import os
from flask import Flask, session, jsonify
from database import db
from flask_cors import CORS

app = Flask(__name__)

# Flask Secret Key & Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'learnathome-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'learnathome.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5000", "http://127.0.0.1:5000"])

# Import & Register Blueprints
from auth import auth_bp
from admin import admin_bp
from tutor import tutor_bp
from student import student_bp
from parent import parent_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(tutor_bp)
app.register_blueprint(student_bp)
app.register_blueprint(parent_bp)

# Register Custom JSON Error Handlers
@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({"success": False, "message": "Access Forbidden (403)"}), 403

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"success": False, "message": "Resource Not Found (404)"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"success": False, "message": "Internal Server Error (500)"}), 500

with app.app_context():
    import models
    db.create_all()
    print("Database tables created successfully!")

@app.route('/')
def home():
    return jsonify({"message": "LearnAtHome Backend Database API is active!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)