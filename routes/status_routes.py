from flask import Blueprint, request, jsonify
from services.user_service import UserService

def status_blueprint(mongo_service, user_service_url):
    status_bp = Blueprint('status', __name__)

    @status_bp.route('/storage-status', methods=['GET'])
    def get_storage_status():
        token = request.headers.get('Authorization', '').split(' ')[-1]
        user = UserService.validate_token(token, user_service_url)
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        email = user['email']
        user_storage = mongo_service.find_user_storage(email)
        
        if not user_storage:
            return jsonify({
                'total_storage': 50 * 1024 * 1024,
                'used_storage': 0,
                'storage_percentage': 0,
                'files': []
            }), 200

        storage_percentage = user_storage['used_storage'] / user_storage['total_storage'] * 100

        return jsonify({
            'total_storage': user_storage['total_storage'],
            'used_storage': user_storage['used_storage'],
            'storage_percentage': storage_percentage,
            'files': user_storage['files']
        }), 200

    return status_bp
