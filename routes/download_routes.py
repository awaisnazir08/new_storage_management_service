from flask import Blueprint, request, jsonify, send_file, Response
from services.user_service import UserService
from services.track_service import TrackService
import io
import os
import mimetypes





def download_blueprint(gcs_service, mongo_service, user_service_url):
    download_bp = Blueprint('download', __name__)

    @download_bp.route('/download/disk/<filename>', methods=['GET'])
    def download_to_client(filename):
        # Get the token from the request headers
        token = request.headers.get('Authorization', '').split(' ')[-1]
        user = UserService.validate_token(token, user_service_url)
        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        email = user['email']
        username = user['username']
        
        filepath = username + '/' + filename
        
        # Check if the user has the file in their storage
        user_storage = mongo_service.find_user_storage(email)

        if not user_storage:
            return jsonify({"error": "User storage not found"}), 404

        # Check if the file is in the user's files list
        file_record = next((file for file in user_storage.get('files', []) if file['filename'] == filepath), None)
        
        print(file_record)
        
        if not file_record:
            return jsonify({"error": "File not found in user's storage"}), 404

        # Download the file from GCS to a temporary path
        destination_path = f"{filename}"  # Example temporary storage location
        downloaded_file = gcs_service.download_to_disk(filepath, destination_path)
        
        if not downloaded_file:
            return jsonify({"error": "File not found in storage"}), 404

        # Send the file to the client for download
        response = send_file(destination_path, as_attachment=True)

        # Optionally, clean up the temporary file after sending
        @response.call_on_close
        def cleanup_temp_file():
            try:
                os.remove(destination_path)
            except Exception as e:
                print(f"Error cleaning up temporary file: {e}")

        return response
    

    @download_bp.route('/stream/video/<filename>', methods=['GET'])
    def stream_video(filename):
        # Get the token from the request headers
        token = request.headers.get('Authorization', '').split(' ')[-1]
        user = UserService.validate_token(token, user_service_url)
        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        email = user['email']
        username = user['username']
        
        filepath = username + '/' + filename
        
        # Check if the user has the file in their storage
        user_storage = mongo_service.find_user_storage(email)

        if not user_storage:
            return jsonify({"error": "User storage not found"}), 404

        # Check if the file is in the user's files list
        file_record = next((file for file in user_storage.get('files', []) if file['filename'] == filepath), None)
        
        if not file_record:
            return jsonify({"error": "File not found in user's storage"}), 404

        # Get the blob for streaming
        blob = gcs_service.get_streaming_blob(filepath)
        
        if not blob:
            return jsonify({"error": "File not found in storage"}), 404

        # Get file size
        file_size = blob.size
        print(f"blob: {blob}")
        print(f"***file_size: {file_size}")
        # Set proper MIME type for MKV files
        # mime_type = 'video/x-matroska'  # Specific MIME type for MKV files
        mime_type, _ = mimetypes.guess_type(filepath)

        # Smaller chunk size for video streaming (1MB)
        CHUNK_SIZE = 512*512 # 1MB in bytes

        # Handle range requests
        range_header = request.headers.get('Range', None)
        byte_start = 0
        byte_end = file_size - 1

        if range_header:
            byte_range = range_header.replace('bytes=', '').split('-')
            byte_start = int(byte_range[0])
            if byte_range[1]:
                byte_end = min(int(byte_range[1]), file_size - 1)

        length = byte_end - byte_start + 1

        def generate():
            """Generator function to stream the file in chunks"""
            remaining_bytes = length
            current_position = byte_start

            while remaining_bytes > 0:
                # Calculate the chunk size for this iteration
                chunk_size = min(CHUNK_SIZE, remaining_bytes)
                
                # Download the specific byte range
                end_position = min(current_position + chunk_size - 1, byte_end)
                chunk = blob.download_as_bytes(start=current_position, end=end_position)
                
                print (f"sending chunks {current_position}-{end_position}")
                yield chunk
                
                current_position += chunk_size
                remaining_bytes -= chunk_size

        # Prepare headers for streaming response
        headers = {
            'Content-Type': mime_type,
            'Accept-Ranges': 'bytes',
            'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
            'Content-Length': str(length),
            'Cache-Control': 'no-cache'
        }

        return Response(
            generate(),
            206 if range_header else 200,
            headers=headers,
            direct_passthrough=True
        )
    
    
    @download_bp.route('/stream/direct/<filename>',methods=['GET'])
    def stream_with_url(filename):
        # Get the token from the request headers
        token = request.headers.get('Authorization', '').split(' ')[-1]
        user = UserService.validate_token(token, user_service_url)
        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        email = user['email']
        username = user['username']
        
        filepath = username + '/' + filename
        
        # Check if the user has the file in their storage
        user_storage = mongo_service.find_user_storage(email)

        if not user_storage:
            return jsonify({"error": "User storage not found"}), 404

        # Check if the file is in the user's files list
        file_record = next((file for file in user_storage.get('files', []) if file['filename'] == filepath), None)
        
        if not file_record:
            return jsonify({"error": "File not found in user's storage"}), 404

        signed_url=gcs_service.generate_download_signed_url_v4(filepath)

        return signed_url
    
    return download_bp

