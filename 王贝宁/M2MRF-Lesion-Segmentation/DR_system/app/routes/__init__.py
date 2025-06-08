from .user_routes import user_bp  # 导入所有蓝图
from .auth_routes import auth_bp
from .auth_routes import doctor_bp
from .auth_routes import patient_bp

def register_routes(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
