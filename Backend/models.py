from database import db
from datetime import datetime

# ==================== MODULE 1: USER MANAGEMENT ====================

class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True, nullable=False)

class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # --- ADDED for Admin Dashboard ---
    # The original schema had no way to display an admin's display name or
    # email, both of which the AdminProfile.vue frontend requires. Added as
    # nullable/defaulted columns so this is a purely additive,
    # backward-compatible change to the existing schema.
    admin_name = db.Column(db.String(100), nullable=False, default='Admin User')
    email = db.Column(db.String(100), unique=True, nullable=True)
    # --- END ADDED ---
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

class Tutor(db.Model):
    __tablename__ = 'tutor'
    tutor_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    tutor_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_no = db.Column(db.String(15))
    experience_years = db.Column(db.Integer)
    bio = db.Column(db.Text, nullable=True)
    subjects_json = db.Column(db.Text, nullable=True)
    education = db.Column(db.String(150), nullable=True)
    hourly_rate = db.Column(db.String(50), nullable=True)
    availability = db.Column(db.String(100), nullable=True)
    languages_json = db.Column(db.Text, nullable=True)
    certificates_json = db.Column(db.Text, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

class Parent(db.Model):
    __tablename__ = 'parent'
    parent_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    parent_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_no = db.Column(db.String(15))
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.parent_id'), nullable=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_no = db.Column(db.String(15))
    school = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)


# ==================== MODULE 2: ACADEMIC MANAGEMENT ====================

class Subject(db.Model):
    __tablename__ = 'subject'
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(50), unique=True, nullable=False)

class StudentSubject(db.Model):
    __tablename__ = 'student_subject'
    student_subject_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('student_id', 'subject_id', name='_student_subject_uc'),)

class Session(db.Model):
    __tablename__ = 'session'
    session_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    session_type = db.Column(db.String(20), default='Regular')  # Regular, One-to-One
    status = db.Column(db.String(20), default='Scheduled')      # Scheduled, Completed, Cancelled, Rescheduled
    # max_seats = db.Column(db.Integer, default=5)

class SessionUpdate(db.Model):
    __tablename__ = 'session_update'
    update_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False, unique=True)
    topics_covered = db.Column(db.Text)
    homework_assigned = db.Column(db.Text)
    next_session_date = db.Column(db.Date)
    notification_time = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== MODULE 3: SESSION ACTIVITIES ====================

class Assignment(db.Model):
    __tablename__ = 'assignment'
    assignment_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    # estimated_time = db.Column(db.String(50), default="20 mins")
    # ai_enabled = db.Column(db.Boolean, default=True)

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submission'
    submission_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending') # Pending, In Progress, Submitted, Completed, Late
    progress_percentage = db.Column(db.Integer, default=0)
    # current_complexity = db.Column(db.String(20), default='Medium') # Easy, Medium, Hard, Advanced
    # consecutive_correct = db.Column(db.Integer, default=0)
    # total_correct = db.Column(db.Integer, default=0)
    # total_attempted = db.Column(db.Integer, default=0)
    tutor_feedback = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint('assignment_id', 'student_id', name='_assignment_student_uc'),)

# class AssignmentQuestion(db.Model):
#     __tablename__ = 'assignment_question'
#     question_id = db.Column(db.Integer, primary_key=True)
#     assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'), nullable=False)
#     complexity_level = db.Column(db.String(20), default='Medium') # Easy, Medium, Hard, Advanced
#     question_text = db.Column(db.Text, nullable=False)
#     option_a = db.Column(db.String(255))
#     option_b = db.Column(db.String(255))
#     option_c = db.Column(db.String(255))
#     option_d = db.Column(db.String(255))
#     correct_option = db.Column(db.String(1), nullable=False) # A, B, C, D
#     explanation = db.Column(db.Text)
#     hint = db.Column(db.Text)

class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'
    progress_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    session_completion_status = db.Column(db.String(30)) # Completed, Partially Completed, Needs Revision
    learning_pace = db.Column(db.String(20))             # Fast, Average, Needs Practice
    tutor_remarks = db.Column(db.Text)

class StudyTip(db.Model):
    __tablename__ = 'study_tip'
    tip_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    tip_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudyResource(db.Model):
    __tablename__ = 'study_resource'
    resource_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    resource_title = db.Column(db.String(150), nullable=False)
    resource_type = db.Column(db.String(20)) # PDF, Video, Website, Notes, Practice Sheet
    resource_link = db.Column(db.String(255))

class TeachingPlan(db.Model):
    __tablename__ = 'teaching_plan'
    plan_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    planned_date = db.Column(db.Date)


# ==================== MODULE 4: ASSESSMENT ====================

class Quiz(db.Model):
    __tablename__ = 'quiz'
    quiz_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    week_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'
    question_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    correct_option = db.Column(db.String(1)) # A, B, C, D
    difficulty = db.Column(db.String(6), default='medium')

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempt'
    attempt_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    score = db.Column(db.Float)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('quiz_id', 'student_id', name='_quiz_student_uc'),)

class WeeklySummary(db.Model):
    __tablename__ = 'weekly_summary'
    summary_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    topics_taught = db.Column(db.Text)
    homework_summary = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== MODULE 5: SCHEDULING ====================

class SessionBooking(db.Model):
    __tablename__ = 'session_booking'
    booking_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    booking_status = db.Column(db.String(20), default='Confirmed')
    __table_args__ = (db.UniqueConstraint('session_id', 'student_id', name='_booking_uc'),)

class MeetingRequest(db.Model):
    __tablename__ = 'meeting_request'
    meeting_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.parent_id'), nullable=True)
    meeting_date = db.Column(db.DateTime, nullable=False)
    meeting_link = db.Column(db.String(255))
    meeting_reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Scheduled')


# ==================== MODULE 6: COMMUNICATION ====================

class Message(db.Model):
    __tablename__ = 'message'
    message_id = db.Column(db.Integer, primary_key=True)
    sender_type = db.Column(db.String(20), nullable=False) # Tutor, Parent, Student
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_type = db.Column(db.String(20), nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(150))
    message = db.Column(db.Text, nullable=False)
    reply_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime)

class FAQ(db.Model):
    __tablename__ = 'faq'
    faq_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))

class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id = db.Column(db.Integer, primary_key=True)
    recipient_type = db.Column(db.String(20), nullable=False) # Parent, Student, Tutor
    recipient_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(30)) # Session Update, Reminder, Weekly Summary, Doubt
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doubt(db.Model):
    __tablename__ = 'doubt'
    doubt_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    subject = db.Column(db.String(50))
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Open', nullable=False) # Open, Answered
    asked_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime, nullable=True)

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_record'
    attendance_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    status = db.Column(db.String(20), default='Present', nullable=False) # Present, Absent, Late
    date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FlashcardDeck(db.Model):
    __tablename__ = 'flashcard_deck'
    deck_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cards = db.relationship('FlashcardItem', backref='deck', cascade='all, delete-orphan', lazy=True)

class FlashcardItem(db.Model):
    __tablename__ = 'flashcard_item'
    card_id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('flashcard_deck.deck_id'), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)