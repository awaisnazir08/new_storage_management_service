import requests
from config import TRACK_SERVICE_URL

class TrackService:
    @staticmethod
    def check_upload_bandwidth(token, file_size):
        try:
            response = requests.post(f"{TRACK_SERVICE_URL}/api/usage/check-upload-bandwidth", 
                                    headers={'Authorization': f'Bearer {token}'},
                                    json={'file_size': file_size})  # Include file_size in the JSON body
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    @staticmethod
    def log_upload(token, file_name, file_size):
        try:
            response = requests.post(f"{TRACK_SERVICE_URL}/api/usage/log-upload",
                                    headers={'Authorization': f"Bearer {token}"},
                                    json = {'file_size': file_size,
                                            "file_name": file_name})
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    @staticmethod
    def check_for_alerts(token):
        try:
            response = requests.get(f"{TRACK_SERVICE_URL}/api/usage/check-usage-alerts",
                                    headers={"Authorization": f"Bearer {token}"})
            
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    @staticmethod
    def log_deletion(token, file_name, file_size):
        try:
            response = requests.post(f"{TRACK_SERVICE_URL}/api/usage/log-deletion",
                                    headers={"Authorization": f"Bearer {token}"},
                                    json = {'file_size': file_size,
                                            "file_name": file_name})
            
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
