# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from ..models import db, User, Doctor, Patient, Diagnose, Lesion, UserRole
from flasgger.utils import swag_from
from datetime import datetime, date
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
import uuid
import base64

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


@auth_bp.route('/submit_diagnosis', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': '提交诊断报告',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'patient_id': {'type': 'integer'},
                    'doctor_id': {'type': 'integer'},
                    'image_path': {'type': 'string'},  # base64编码的图片数据
                    'diagnose_date': {'type': 'string', 'format': 'date-time'},
                    'confirmed': {'type': 'boolean'}
                },
                'required': ['patient_id', 'doctor_id', 'image_path']
            }
        }
    ],
    'responses': {
        200: {
            'description': '提交成功'
        },
        400: {
            'description': '参数错误'
        }
    }
})
def submit_diagnosis():
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['patient_id', 'doctor_id', 'image_path']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 创建保存图片的文件夹
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'diagnosis')
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        # 生成唯一的文件名
        filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # 解码base64图片数据并保存
        try:
            image_data = data['image_path'].split(',')[1]  # 移除 "data:image/jpeg;base64," 前缀
            image_bytes = base64.b64decode(image_data)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
        except Exception as e:
            return jsonify({'error': f'图片保存失败: {str(e)}'}), 400
        
        # 创建诊断记录
        diagnosis = Diagnose(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            image_path=os.path.join('uploads', 'diagnosis', filename),  # 存储相对路径
            diagnose_date=datetime.now() if 'diagnose_date' not in data else datetime.fromisoformat(data['diagnose_date']),
            confirmed=data.get('confirmed', False)
        )
        
        db.session.add(diagnosis)
        db.session.commit()
        
        return jsonify({
            'message': '诊断报告提交成功',
            'diagnosis_id': diagnosis.diagnosis_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/diagnosis/<int:diagnosis_id>', methods=['GET'])
@swag_from({
    'tags': ['Auth'],
    'summary': '获取诊断报告详情',
    'parameters': [
        {
            'name': 'diagnosis_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': '获取成功'
        },
        404: {
            'description': '报告不存在'
        }
    }
})
def get_diagnosis_detail(diagnosis_id):
    try:
        # 查询诊断记录
        diagnosis = db.session.query(
            Diagnose,
            Patient.name.label('patient_name'),
            Patient.patient_id,
            Doctor.name.label('doctor_name'),
            Doctor.doctor_id
        ).join(
            Patient, Diagnose.patient_id == Patient.patient_id
        ).join(
            Doctor, Diagnose.doctor_id == Doctor.doctor_id
        ).filter(
            Diagnose.diagnosis_id == diagnosis_id
        ).first()

        if not diagnosis:
            return jsonify({'error': '报告不存在'}), 404

        # 生成报告编号
        report_id = f"R{diagnosis.Diagnose.diagnose_date.strftime('%Y%m%d')}{diagnosis.Diagnose.diagnosis_id:03d}"

        # 格式化日期和时间
        check_date = diagnosis.Diagnose.diagnose_date.strftime('%Y-%m-%d')
        check_time = diagnosis.Diagnose.diagnose_date.strftime('%H:%M:%S')

        return jsonify({
            'report_id': report_id,
            'patient_name': diagnosis.patient_name,
            'patient_id': diagnosis.patient_id,
            'doctor_name': diagnosis.doctor_name,
            'doctor_id': diagnosis.doctor_id,
            'check_date': check_date,
            'check_time': check_time,
            'status': '已审核' if diagnosis.Diagnose.confirmed else '待审核',
            'image_path': diagnosis.Diagnose.image_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/diagnosis/<int:diagnosis_id>/confirm', methods=['PUT'])
@swag_from({
    'tags': ['Auth'],
    'summary': '修改诊断报告审核状态',
    'parameters': [
        {
            'name': 'diagnosis_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': '修改成功'
        },
        404: {
            'description': '报告不存在'
        }
    }
})
def confirm_diagnosis(diagnosis_id):
    try:
        diagnosis = Diagnose.query.get(diagnosis_id)
        if not diagnosis:
            return jsonify({'error': '报告不存在'}), 404

        diagnosis.confirmed = True
        db.session.commit()

        return jsonify({
            'message': '审核状态已更新',
            'diagnosis_id': diagnosis_id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/diagnosis/<int:diagnosis_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Auth'],
    'summary': '删除诊断报告',
    'parameters': [
        {
            'name': 'diagnosis_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': '删除成功'
        },
        404: {
            'description': '报告不存在'
        }
    }
})
def delete_diagnosis(diagnosis_id):
    try:
        diagnosis = Diagnose.query.get(diagnosis_id)
        if not diagnosis:
            return jsonify({'error': '报告不存在'}), 404

        # 删除图片文件
        if diagnosis.image_path:
            try:
                image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), diagnosis.image_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"删除图片文件失败: {str(e)}")

        # 删除数据库记录
        db.session.delete(diagnosis)
        db.session.commit()

        return jsonify({
            'message': '报告已退回',
            'diagnosis_id': diagnosis_id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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

    return jsonify([
    {
        "patient_name": row.patient_name,
        "diagnosis_id": row.diagnosis_id,
        "diagnose_date": row.diagnose_date.strftime('%Y-%m-%d') if row.diagnose_date else None,
        "lesion_count": row.lesion_count,
        "confirmed": row.confirmed
    }
    for row in results
    ])


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
         .order_by(Diagnose.diagnosis_time.desc())
         .limit(3)
         .all()
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

    return jsonify([
    {
        "patient_name": row.patient_name,
        "diagnosis_id": row.diagnosis_id,
        "diagnose_date": row.diagnose_date.strftime('%Y-%m-%d') if row.diagnose_date else None,
        "lesion_count": row.lesion_count,
        "confirmed": row.confirmed
    }
    for row in query.all()
])


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
            Diagnose.image_path.label('report_image'),
            Diagnose.diagnosis_id
        ).outerjoin(Lesion, Diagnose.diagnosis_id == Lesion.diagnosis_id)
         .join(Doctor, Diagnose.doctor_id == Doctor.doctor_id)
         .filter(Diagnose.patient_id == patient_id)
         .group_by(Diagnose.diagnosis_id, Diagnose.diagnose_date, Diagnose.confirmed, Doctor.name, Diagnose.image_path)
         .order_by(Diagnose.diagnose_date.desc()).all()
    )

    return jsonify([{
        "report_date": row.report_date.strftime('%Y-%m-%d') if row.report_date else None,
        "lesion_count": row.lesion_count,
        "is_confirmed": row.is_confirmed,
        "doctor_name": row.doctor_name,
        "report_image": row.report_image,
        "diagnosis_id": row.diagnosis_id
    } for row in results])
