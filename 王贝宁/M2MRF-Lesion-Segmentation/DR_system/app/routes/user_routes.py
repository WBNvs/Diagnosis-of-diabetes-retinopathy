from flask import Blueprint, request, jsonify
from ..models import db, User, UserRole
from flasgger.utils import swag_from

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


@user_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['User'],
    'summary': '获取所有用户',
    'responses': {
        200: {
            'description': '用户列表',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'user_id': {'type': 'integer'},
                        'username': {'type': 'string'},
                        'role': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_users():
    users = User.query.all()
    return jsonify([
        {
            'user_id': u.user_id,
            'username': u.username,
            'role': u.role.value
        } for u in users
    ])


@user_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'summary': '创建新用户',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'},
                    'role': {'type': 'string', 'enum': ['patient', 'doctor']}
                },
                'required': ['username', 'password', 'role']
            }
        }
    ],
    'responses': {
        201: {
            'description': '用户创建成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'user_id': {'type': 'integer'}
                }
            }
        },
        400: {
            'description': '无效的角色'
        }
    }
})
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if role not in ['patient', 'doctor']:
        return jsonify({'error': 'Invalid role'}), 400

    user = User(username=username, password=password, role=UserRole(role))
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created', 'user_id': user.user_id}), 201
