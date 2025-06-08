# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from ..models import db, User, Doctor, Patient, Diagnose, Lesion, UserRole
from flasgger.utils import swag_from
from datetime import datetime, date
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': '用户登录',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': '登录成功，返回 token 信息'
        },
        401: {
            'description': '用户名或密码错误'
        }
    }
})
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or user.password != data.get('password'):
        return jsonify({'error': 'Invalid username or password'}), 401

    role = user.role.value
    result = {
        'user_id': user.user_id,
        'role': role
    }

    if role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.user_id).first()
        result['doctor_id'] = doctor.doctor_id
    elif role == 'patient':
        patient = Patient.query.filter_by(user_id=user.user_id).first()
        result['patient_id'] = patient.patient_id

    return jsonify({'token': result})


# Doctor APIs
doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/doctor')

@doctor_bp.route('/stats', methods=['GET'])
@swag_from({
    'tags': ['Doctor'],
    'summary': '医生诊断统计',
    'parameters': [
        {
            'name': 'doctor_id',
            'in': 'query',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {200: {'description': '统计信息'}}
})
def doctor_stats():
    doctor_id = request.args.get('doctor_id', type=int)
    today = date.today()
    month_start = today.replace(day=1)

    total_today = Diagnose.query.filter_by(doctor_id=doctor_id, confirmed=True).filter(func.date(Diagnose.diagnose_date) == today).count()
    pending = Diagnose.query.filter_by(doctor_id=doctor_id, confirmed=False).count()
    confirmed_this_month = Diagnose.query.filter(Diagnose.doctor_id == doctor_id, Diagnose.confirmed == True, Diagnose.diagnose_date >= month_start).count()

    abnormal = Diagnose.query.filter(
        Diagnose.doctor_id == doctor_id,
        Diagnose.confirmed == True,
        Diagnose.diagnosis_id.in_(
            db.session.query(Lesion.diagnosis_id).distinct()
        )
    ).count()

    return jsonify({
        'today_confirmed': total_today,
        'pending': pending,
        'abnormal_cases': abnormal,
        'confirmed_this_month': confirmed_this_month
    })


@doctor_bp.route('/pending_cases', methods=['GET'])
@swag_from({'tags': ['Doctor'], 'summary': '获取待处理病例列表'})
def pending_cases():
    doctor_id = request.args.get('doctor_id', type=int)
    results = (
        db.session.query(
            Patient.name.label('patient_name'),
            Diagnose.diagnosis_id,
            Diagnose.diagnose_date,
            func.count(Lesion.lesion_id).label('lesion_count'),
            Diagnose.confirmed
        ).join(Patient, Diagnose.patient_id == Patient.patient_id)
         .outerjoin(Lesion, Diagnose.diagnosis_id == Lesion.diagnosis_id)
         .filter(Diagnose.doctor_id == doctor_id, Diagnose.confirmed == False)
         .group_by(Diagnose.diagnosis_id, Patient.name, Diagnose.diagnose_date, Diagnose.confirmed)
         .order_by(Diagnose.diagnose_date.desc()).all()
    )

    return jsonify([dict(row._mapping) for row in results])


@doctor_bp.route('/recent', methods=['GET'])
@swag_from({'tags': ['Doctor'], 'summary': '获取今日已确认的最近诊断记录'})
def recent_diagnoses():
    doctor_id = request.args.get('doctor_id', type=int)
    today = date.today()
    diagnoses = (
        db.session.query(
            Patient.name.label('patient_name'),
            func.date_format(Diagnose.diagnosis_time, '%H:%i:%s').label('diagnosis_time_only')
        ).join(Patient, Diagnose.patient_id == Patient.patient_id)
         .filter(Diagnose.doctor_id == doctor_id, Diagnose.confirmed == True, func.date(Diagnose.diagnosis_time) == today)
         .order_by(Diagnose.diagnosis_time.desc()).all()
    )

    return jsonify([dict(row._mapping) for row in diagnoses])


@doctor_bp.route('/history', methods=['GET'])
@swag_from({'tags': ['Doctor'], 'summary': '获取诊断历史（全部、待审核、已审核）'})
def diagnosis_history():
    doctor_id = request.args.get('doctor_id', type=int)
    confirmed = request.args.get('confirmed')  # true/false/null

    query = (
        db.session.query(
            Patient.name.label('patient_name'),
            Diagnose.diagnosis_id,
            Diagnose.diagnose_date,
            func.count(Lesion.lesion_id).label('lesion_count'),
            Diagnose.confirmed
        ).join(Patient, Diagnose.patient_id == Patient.patient_id)
         .outerjoin(Lesion, Diagnose.diagnosis_id == Lesion.diagnosis_id)
         .filter(Diagnose.doctor_id == doctor_id)
         .group_by(Diagnose.diagnosis_id, Patient.name, Diagnose.diagnose_date, Diagnose.confirmed)
         .order_by(Diagnose.diagnose_date.desc())
    )

    if confirmed == 'true':
        query = query.filter(Diagnose.confirmed == True)
    elif confirmed == 'false':
        query = query.filter(Diagnose.confirmed == False)

    return jsonify([dict(row._mapping) for row in query.all()])


# Patient APIs
patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@patient_bp.route('/reports', methods=['GET'])
@swag_from({'tags': ['Patient'], 'summary': '获取我的报告'})
def patient_reports():
    patient_id = request.args.get('patient_id', type=int)

    results = (
        db.session.query(
            Diagnose.diagnose_date.label('report_date'),
            func.count(Lesion.lesion_id).label('lesion_count'),
            Diagnose.confirmed.label('is_confirmed'),
            Doctor.name.label('doctor_name'),
            Diagnose.image_path.label('report_image')
        ).outerjoin(Lesion, Diagnose.diagnosis_id == Lesion.diagnosis_id)
         .join(Doctor, Diagnose.doctor_id == Doctor.doctor_id)
         .filter(Diagnose.patient_id == patient_id)
         .group_by(Diagnose.diagnosis_id, Diagnose.diagnose_date, Diagnose.confirmed, Doctor.name, Diagnose.image_path)
         .order_by(Diagnose.diagnose_date.desc()).all()
    )

    return jsonify([dict(row._mapping) for row in results])
