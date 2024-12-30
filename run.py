from flask import Flask
from config import USER_SERVICE_URL, MONGODB_URI, GCS_BUCKET
from services.gcs_service import GCSService
from services.mongo_service import MongoService
from routes.upload_routes import upload_blueprint
from routes.status_routes import status_blueprint
from routes.delete_routes import delete_blueprint
from routes.download_routes import download_blueprint
from flask_cors import CORS  # Import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Service initializations
gcs_service = GCSService(GCS_BUCKET)
mongo_service = MongoService(MONGODB_URI)

# Register Blueprints (routes)
app.register_blueprint(upload_blueprint(gcs_service, mongo_service, USER_SERVICE_URL))
app.register_blueprint(status_blueprint(mongo_service, USER_SERVICE_URL))
app.register_blueprint(delete_blueprint(gcs_service, mongo_service, USER_SERVICE_URL))
app.register_blueprint(download_blueprint(gcs_service, mongo_service, USER_SERVICE_URL))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)