from flask import Flask, send_from_directory
from .extensions import db
from .routes import register_routes
from flask_cors import CORS
from flasgger import Swagger
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://wbn:Wbn123456@localhost:3306/medicaldb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # 配置静态文件服务
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # 添加静态文件路由
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    db.init_app(app)
    register_routes(app)

    # 初始化 Swagger
    Swagger(app)

    with app.app_context():
        db.create_all()  # 初始化表结构（第一次用）

    return app