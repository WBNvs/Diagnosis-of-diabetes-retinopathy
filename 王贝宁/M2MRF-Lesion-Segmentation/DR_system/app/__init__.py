from flask import Flask
from .extensions import db
from .routes import register_routes

from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://wbn:Wbn123456@localhost:3306/medicaldb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    register_routes(app)

    # 初始化 Swagger
    Swagger(app)

    with app.app_context():
        db.create_all()  # 初始化表结构（第一次用）

    return app
