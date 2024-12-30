from flask import Blueprint, request, jsonify
from services.user_service import UserService
from services.track_service import TrackService
import requests

def upload_blueprint(gcs_service, mongo_service, user_service_url):
    upload_bp = Blueprint('upload', __name__)

    @upload_bp.route('/upload', methods=['POST'])
    def upload_video():
        token = request.headers.get('Authorization', '').split(' ')[-1]
        user = UserService.validate_token(token, user_service_url)

        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        
        email = user['email']
        username = user['username']
        user_storage = mongo_service.find_user_storage(email)
        
        if not user_storage:
            user_storage = mongo_service.initialize_user_storage(email, 50 * 1024 * 1024)  # 50MB

        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        file_size = len(file.read())
        file.seek(0)

        # Check if file with the same name already exists
        existing_files = user_storage.get('files', [])
        
        if any(f['filename'] == f"{username}/{file.filename}" for f in existing_files):
            return jsonify({"error": "File with the same name already exists."}), 409

        if user_storage['used_storage'] + file_size > user_storage['total_storage']:
            return jsonify({"error": "Exceeds storage limit, cannot upload video..!!"}), 403
        
        allow_upload = TrackService.check_upload_bandwidth(token, file_size)
        
        if not allow_upload:
            return jsonify({"error": "Bandwidth limit exceeded or some internal upload error"}), 403

        filename = f"{username}/{file.filename}"
        gcs_service.upload_file(filename, file)

        mongo_service.update_storage(email, {
            '$inc': {'used_storage': file_size},
            '$push': {'files': {'filename': filename, 'size': file_size}}
        })
        
        usage_record = TrackService.log_upload(token, file.filename, file_size)
        
        if not usage_record:
            return jsonify({"error": "Usage record couldn't be inserted or updated..!!"}), 400
        
        return_dict = {'storage_80_alert': False, 'bandwidth_80_alert': False} 
        
        storage_percentage_used = (user_storage['used_storage'] + file_size) / user_storage['total_storage'] * 100
        
        if storage_percentage_used >= 80:
            return_dict['storage_80_alert'] = True
        return_dict['storage_percentage_used'] = storage_percentage_used
        
        alert_logs = TrackService.check_for_alerts(token)
        
        if alert_logs:
            return_dict.update(alert_logs)
            if alert_logs['bandwidth_checks']['bandwidth_limit_approaching']:
                return_dict['bandwidth_80_alert'] = True
        
        return_dict['message'] = "File uploaded successfully"
        
        return jsonify(return_dict), 200

    return upload_bp
