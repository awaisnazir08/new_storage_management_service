from flask import Blueprint, request, jsonify
from services.user_service import UserService
from services.track_service import TrackService

def delete_blueprint(gcs_service, mongo_service, user_service_url):
    delete_bp = Blueprint('delete', __name__)

    @delete_bp.route('/delete-file', methods=['DELETE'])
    def delete_file():
        token = request.headers.get('Authorization', '').split(' ')[-1]
        user = UserService.validate_token(token, user_service_url)
        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        filename = request.json.get('filename')
        if not filename:
            return jsonify({"error": "No filename provided"}), 400

        username = user['username']
        email = user['email']
        full_filename = f"{username}/{filename}"

        try:
            # Delete file from Google Cloud Storage
            gcs_service.delete_file(full_filename)

            # Find and update user's storage
            user_storage = mongo_service.find_user_storage(email)
            file_to_remove = next((f for f in user_storage['files'] if f['filename'] == full_filename), None)

            if file_to_remove:
                mongo_service.update_storage(email, {
                    '$inc': {'used_storage': -file_to_remove['size']},
                    '$pull': {'files': {'filename': full_filename}}
                })

            delete_log = TrackService.log_deletion(token, filename, file_to_remove['size'])
            
            print(delete_log)
            if delete_log:
                # Add the message to the dictionary
                delete_log.update({"message": "File deleted successfully"})
                return jsonify(delete_log), 200            
            return jsonify({"message": "File deleted successfully"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return delete_bp
