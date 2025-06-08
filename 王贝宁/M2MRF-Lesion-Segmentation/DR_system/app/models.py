from .extensions import db
from sqlalchemy import Enum
import enum

# 定义角色枚举
class UserRole(enum.Enum):
    patient = 'patient'
    doctor = 'doctor'

class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(Enum(UserRole), nullable=False)

    # 关系
    patient = db.relationship('Patient', backref='user', uselist=False, cascade="all, delete")
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade="all, delete")

class Patient(db.Model):
    __tablename__ = 'Patient'
    patient_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('male', 'female'), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    contact_info = db.Column(db.String(255))

    diagnoses = db.relationship('Diagnose', backref='patient', cascade="all, delete")

class Doctor(db.Model):
    __tablename__ = 'Doctor'
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(255))

    diagnoses = db.relationship('Diagnose', backref='doctor', cascade="all, delete")

class Diagnose(db.Model):
    __tablename__ = 'Diagnose'
    diagnosis_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patient.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('Doctor.doctor_id'), nullable=False)
    diagnosis_time = db.Column(db.DateTime, server_default=db.func.now())
    image_path = db.Column(db.String(255))
    confirmed = db.Column(db.Boolean, default=False)
    diagnose_date = db.Column(db.Date, nullable=False)

    lesions = db.relationship('Lesion', backref='diagnosis', cascade="all, delete")

class Lesion(db.Model):
    __tablename__ = 'Lesion'
    lesion_id = db.Column(db.Integer, primary_key=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('Diagnose.diagnosis_id'), nullable=False)
