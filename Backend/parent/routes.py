from datetime import datetime, date
from flask import jsonify, request, session
from parent import parent_bp
from database import db
from models import Parent, Student, WeeklySummary, QuizAttempt, AttendanceRecord, TeachingPlan, MeetingRequest, Tutor, Session, SessionBooking, Subject, StudentSubject, Message, Notification
from decorators import parent_required
from utils import decode_jwt_token


def current_parent():
    auth=request.headers.get('Authorization','')
    if auth.startswith('Bearer '):
        payload=decode_jwt_token(auth.split(' ',1)[1])
        if payload and payload.get('role')=='Parent':
            p=db.session.get(Parent,payload.get('user_id'))
            if p:return p
    uid=session.get('user_id')
    if uid and session.get('role')=='Parent':return db.session.get(Parent,uid)
    return None


def ok(data=None,message=None,status=200):
    p={'success':True,'status':'success'}
    if message:p['message']=message
    if data is not None:p['data']=data
    return jsonify(p),status

def fail(message,status=400):return jsonify({'success':False,'status':'error','message':message}),status


@parent_bp.route('/health', methods=['GET'])
def health_check():return ok(message='Parent API blueprint working!')


@parent_bp.route('/profile/<int:parent_id>', methods=['GET','PUT'])
@parent_required
def profile(parent_id):
    parent=current_parent()
    if not parent or parent.parent_id!=parent_id:return fail('Unauthorized parent access',403)
    if request.method=='PUT':
        d=request.get_json(silent=True) or {}
        if 'parent_name' in d:parent.parent_name=d['parent_name']
        if 'phone_no' in d:parent.phone_no=d['phone_no']
        db.session.commit();return ok({'parent_id':parent.parent_id,'parent_name':parent.parent_name,'email':parent.email,'phone_no':parent.phone_no},'Parent profile updated')
    children=Student.query.filter_by(parent_id=parent_id).all()
    return ok({'parent_id':parent.parent_id,'parent_name':parent.parent_name,'email':parent.email,'phone_no':parent.phone_no,'status':parent.status,'linked_children':[{'student_id':c.student_id,'student_name':c.student_name,'email':c.email,'status':c.status,'tutor_id':((Session.query.join(SessionBooking, SessionBooking.session_id==Session.session_id).filter(SessionBooking.student_id==c.student_id).order_by(Session.session_date.desc()).first().tutor_id) if Session.query.join(SessionBooking, SessionBooking.session_id==Session.session_id).filter(SessionBooking.student_id==c.student_id).first() else None)} for c in children]})


@parent_bp.route('/overview/<int:parent_id>', methods=['GET'])
@parent_required
def overview(parent_id):
    parent=current_parent()
    if not parent or parent.parent_id!=parent_id:return fail('Unauthorized parent access',403)
    children=Student.query.filter_by(parent_id=parent_id).all(); ids=[c.student_id for c in children]
    latest=WeeklySummary.query.filter(WeeklySummary.student_id.in_(ids)).order_by(WeeklySummary.created_at.desc()).first() if ids else None
    return ok({'parent_id':parent.parent_id,'parent_name':parent.parent_name,'total_children':len(children),'children':[{'student_id':c.student_id,'student_name':c.student_name,'status':c.status} for c in children],'latest_summary':{'topics_taught':latest.topics_taught if latest else 'No summary yet','homework':latest.homework_summary if latest else 'No homework recorded','areas_for_improvement':latest.areas_for_improvement if latest else 'No remarks yet'}})


@parent_bp.route('/meeting-request', methods=['POST'])
@parent_required
def request_meeting():
    parent=current_parent(); d=request.get_json(silent=True) or {}
    if not parent:return fail('Parent not logged in',401)
    if int(d.get('parent_id',-1))!=parent.parent_id:return fail('Unauthorized parent access',403)
    required=['tutor_id','student_id','preferred_date','preferred_time']
    if any(x not in d for x in required):return fail('Missing required meeting fields')
    child=db.session.get(Student,int(d['student_id']))
    if not child or child.parent_id!=parent.parent_id:return fail('Child is not linked to this parent',403)
    try:dt=datetime.strptime(f"{d['preferred_date']} {d['preferred_time']}",'%Y-%m-%d %H:%M')
    except ValueError:return fail('Invalid date/time')
    m=MeetingRequest(tutor_id=int(d['tutor_id']),student_id=child.student_id,parent_id=parent.parent_id,meeting_date=dt,meeting_reason=d.get('notes',''),status='Pending');db.session.add(m);db.session.commit();return ok({'meeting_id':m.meeting_id,'meeting_date':m.meeting_date.isoformat(),'status':m.status},'Meeting request submitted',201)


@parent_bp.route('/meetings/<int:parent_id>', methods=['GET'])
@parent_required
def meetings(parent_id):
    parent=current_parent()
    if not parent or parent.parent_id!=parent_id:return fail('Unauthorized parent access',403)
    rows=MeetingRequest.query.filter_by(parent_id=parent_id).order_by(MeetingRequest.meeting_date.desc()).all()
    data=[]
    for m in rows:
        st=db.session.get(Student,m.student_id);t=db.session.get(Tutor,m.tutor_id)
        data.append({'meeting_id':m.meeting_id,'student_id':m.student_id,'student_name':st.student_name if st else None,'tutor_id':m.tutor_id,'tutor_name':t.tutor_name if t else None,'meeting_date':m.meeting_date.isoformat(),'meeting_link':m.meeting_link,'meeting_reason':m.meeting_reason,'status':m.status})
    return ok(data)


@parent_bp.route('/child-progress/<int:parent_id>/<int:student_id>', methods=['GET'])
@parent_required
def child_progress(parent_id,student_id):
    parent=current_parent();child=db.session.get(Student,student_id)
    if not parent or parent.parent_id!=parent_id:return fail('Unauthorized parent access',403)
    if not child or child.parent_id!=parent_id:return fail('Child not found for this parent',404)
    attendance=AttendanceRecord.query.filter_by(student_id=student_id).all(); present=sum(a.status=='Present' for a in attendance); rate=round(present/len(attendance)*100) if attendance else 0
    attempts=QuizAttempt.query.filter_by(student_id=student_id).order_by(QuizAttempt.attempted_at.desc()).limit(5).all(); quiz_scores=[]
    for a in attempts:
        q=__import__('models').Quiz.query.get(a.quiz_id); sub=db.session.get(Subject,q.subject_id).subject_name if q and db.session.get(Subject,q.subject_id) else 'General'
        quiz_scores.append({'subject':sub,'topic':q.title if q else 'Quiz','score':f'{a.score}/100' if a.score is not None else 'N/A','date':a.attempted_at.strftime('%Y-%m-%d') if a.attempted_at else ''})
    remarks=WeeklySummary.query.filter_by(student_id=student_id).order_by(WeeklySummary.created_at.desc()).limit(3).all()
    return ok({'student_id':child.student_id,'student_name':child.student_name,'attendance_rate':f'{rate}%','recent_quiz_scores':quiz_scores,'tutor_remarks':[{'tutor_name':(db.session.get(Tutor,r.tutor_id).tutor_name if db.session.get(Tutor,r.tutor_id) else 'Tutor'),'subject':'General','remark':r.areas_for_improvement or r.topics_taught,'date':r.created_at.strftime('%Y-%m-%d')} for r in remarks]})


@parent_bp.route('/curriculum/<int:student_id>', methods=['GET'])
@parent_required
def curriculum(student_id):
    parent=current_parent();child=db.session.get(Student,student_id)
    if not parent or not child or child.parent_id!=parent.parent_id:return fail('Child not found for this parent',404)
    subject_ids={x.subject_id for x in StudentSubject.query.filter_by(student_id=student_id).all()}
    plans=TeachingPlan.query.filter(TeachingPlan.subject_id.in_(subject_ids)).order_by(TeachingPlan.planned_date).all() if subject_ids else []
    data=[{'month':p.month,'subject':db.session.get(Subject,p.subject_id).subject_name if db.session.get(Subject,p.subject_id) else 'General','topics':[p.topic_name],'status':'Planned'} for p in plans]
    return ok({'student_id':student_id,'student_name':child.student_name,'curriculum_plan':data})


@parent_bp.route('/schedule/<int:parent_id>', methods=['GET'])
@parent_required
def schedule(parent_id):
    parent=current_parent()
    if not parent or parent.parent_id!=parent_id:return fail('Unauthorized parent access',403)
    children=Student.query.filter_by(parent_id=parent_id).all(); ids=[c.student_id for c in children]
    rows=SessionBooking.query.filter(SessionBooking.student_id.in_(ids)).join(Session).order_by(Session.session_date,Session.start_time).all() if ids else []
    data=[]
    for b in rows:
        s=b.session;st=db.session.get(Student,b.student_id);t=db.session.get(Tutor,s.tutor_id);sub=db.session.get(Subject,s.subject_id)
        data.append({'session_id':s.session_id,'student_id':b.student_id,'student_name':st.student_name if st else None,'subject':sub.subject_name if sub else 'General','tutor':t.tutor_name if t else 'Tutor','date':s.session_date.isoformat(),'start_time':s.start_time.strftime('%H:%M'),'end_time':s.end_time.strftime('%H:%M'),'status':s.status,'booking_status':b.booking_status,'meeting_url':s.meeting_url,'meetingUrl':s.meeting_url})
    return ok(data)


@parent_bp.route('/messages/<int:parent_id>', methods=['GET'])
@parent_required
def messages(parent_id):
    parent=current_parent()
    if not parent or parent.parent_id!=parent_id:return fail('Unauthorized parent access',403)
    rows=Message.query.filter(((Message.sender_type=='Parent')&(Message.sender_id==parent_id))|((Message.receiver_type=='Parent')&(Message.receiver_id==parent_id))).order_by(Message.sent_at).all()
    return ok([{'message_id':m.message_id,'sender_type':m.sender_type,'sender_id':m.sender_id,'receiver_type':m.receiver_type,'receiver_id':m.receiver_id,'subject':m.subject,'message':m.message,'sent_at':m.sent_at.isoformat() if m.sent_at else None,'reply_message':m.reply_message} for m in rows])


@parent_bp.route('/notifications/<int:parent_id>', methods=['GET'])
@parent_required
def notifications(parent_id):
    parent=current_parent()
    if not parent or parent.parent_id!=parent_id:return fail('Unauthorized parent access',403)
    rows=Notification.query.filter_by(recipient_type='Parent',recipient_id=parent_id).order_by(Notification.created_at.desc()).all()
    return ok([{'id':n.notification_id,'title':n.title,'message':n.message,'is_read':n.is_read,'created_at':n.created_at.isoformat()} for n in rows])
