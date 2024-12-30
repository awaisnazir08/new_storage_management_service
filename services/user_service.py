import requests

class UserService:
    @staticmethod
    def validate_token(token, user_service_url):
        try:
            response = requests.get(f"{user_service_url}/api/users/profile", 
                                    headers={'Authorization': f'Bearer {token}'})
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
