"""Initialize a clean LearnAtHome database without sample users/activity."""
from werkzeug.security import generate_password_hash
from app import app
from database import db
from models import Role, Subject, Admin
with app.app_context():
    db.create_all()
    roles={}
    for name in ('Admin','Tutor','Parent','Student'):
        role=Role.query.filter_by(role_name=name).first()
        if not role:
            role=Role(role_name=name);db.session.add(role);db.session.flush()
        roles[name]=role
    if not Admin.query.filter_by(username='admin').first():
        db.session.add(Admin(role_id=roles['Admin'].role_id,username='admin',password_hash=generate_password_hash('admin123'),admin_name='Admin User',email='admin@learnathome.com'))
    for name in ('English','Mathematics','Physics','Science','Chemistry','Biology'):
        if not Subject.query.filter_by(subject_name=name).first(): db.session.add(Subject(subject_name=name))
    db.session.commit()
    print('Clean database initialized: roles, subjects and admin only.')
