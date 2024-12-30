# Video Storage Management Microservice

This microservice provides APIs to manage video storage for authenticated users. It enables video uploads, downloads, streams, deletions, and storage status tracking. The microservice integrates with a User Account Management Service for authentication and authorization.

## Features
- **Upload Video**: Uploads video files to Google Cloud Storage.
- **Delete Video**: Deletes video files from Google Cloud Storage.
- **Check Storage Status**: Retrieves the user's current storage usage and details.
- **Download Video**: Downloads the video files which the user wants from the Google Cloud Storage.
- **Stream Video**: Streams the video files which the user wants from the Google Cloud Storage Bucket.

## Requirements

### System Requirements
- Python 3.8+
- Flask 2.0+
- MongoDB for user storage management
- Google Cloud Storage bucket

### Python Libraries
- `flask`
- `google-cloud-storage`
- `pymongo`
- `requests`

### Environment Setup
1. Create a Google Cloud Storage bucket and ensure the associated service account has the required permissions (e.g., `Storage Object Admin`).
2. Set up a MongoDB database to store user storage details.
3. Integrate the User Account Management Service for token validation.

## API Endpoints

### 1. Upload Video
**Endpoint:** `/upload`  
**Method:** `POST`

This README provides details about the `/upload` endpoint, which is part of the `upload` blueprint. The endpoint facilitates video uploads to Google Cloud Storage (GCS), ensuring proper user authentication, storage limit enforcement, and bandwidth tracking.

### **Headers**
- **Authorization:** `Bearer <JWT token>`  
  Used to authenticate the user.

### **Form Data**
- **file** (required): The video file to be uploaded.

---

## **Response**

### **Success (200)**
Returns a JSON object indicating the successful upload, along with storage and bandwidth usage details.

#### **Example**
```json
{
  "storage_80_alert": false,
  "bandwidth_80_alert": false,
  "storage_percentage_used": 65.7,
  "message": "File uploaded successfully"
}
```

### **Client Errors**
- **401 Unauthorized**  
  If the token is invalid or the user is not authenticated.
  ```json
  {"error": "Unauthorized"}
  ```

- **400 Bad Request**  
  If the request does not include a `file` field.
  ```json
  {"error": "No file part"}
  ```

- **403 Forbidden**  
  If the file exceeds the user's storage limit or the bandwidth limit.
  ```json
  {"error": "Exceeds storage limit, cannot upload video..!!"}
  ```
  ```json
  {"error": "Bandwidth limit exceeded or some internal upload error"}
  ```

- **409 Conflict**  
  If a file with the same name already exists.
  ```json
  {"error": "File with the same name already exists."}
  ```

- **400 Bad Request**  
  If the usage record could not be updated.
  ```json
  {"error": "Usage record couldn't be inserted or updated..!!"}
  ```

---

## **Key Features**

1. **User Authentication**  
   Uses the provided JWT token to authenticate the user via `UserService`.

2. **Storage Management**  
   - Verifies if the user has sufficient storage.
   - Initializes user storage to 50 MB if not already set.

3. **File Validation**  
   - Checks if a file is provided.
   - Prevents duplicate file uploads by verifying file names.

4. **Bandwidth Monitoring**  
   - Ensures uploads do not exceed the user's bandwidth limit.
   - Logs usage and checks for alerts related to bandwidth.

5. **Alerts and Usage Metrics**  
   - Alerts the user if storage or bandwidth usage exceeds 80%.
   - Provides real-time storage percentage usage.

---

## **Error Handling**

- Graceful error responses for unauthorized access, invalid file uploads, storage or bandwidth limit violations, and system-level issues.
- Prevents duplicate files with the same name from being uploaded.

---

## **Dependencies**

- **`gcs_service`**  
  Manages interactions with Google Cloud Storage for file uploads.

- **`mongo_service`**  
  Handles user storage management and database operations.

- **`user_service_url`**  
  The URL for user authentication and token validation.

- **`TrackService`**  
  Tracks and manages bandwidth usage, logs uploads, and generates alerts.

---

## **Setup and Usage**

### **Blueprint Registration**
Ensure the `upload` blueprint is registered in your Flask application:
```python
from upload import upload_blueprint
app.register_blueprint(upload_blueprint(gcs_service, mongo_service, user_service_url))
```

---

## **Examples**

### **Request Example**
```bash
curl -X POST "https://example.com/upload" \
-H "Authorization: Bearer <JWT token>" \
-F "file=@video.mp4"
```

### **Response Example**
```json
{
  "storage_80_alert": true,
  "bandwidth_80_alert": false,
  "storage_percentage_used": 85.2,
  "message": "File uploaded successfully"
}
```

### 2. Delete Video
**Endpoint:** `/delete-file`  
**Method:** `DELETE`

**Headers:**
- `Authorization`: `Bearer <user_token>`

**Body (JSON):**
- `filename`: Name of the file to be deleted.

**Responses:**
- **200 OK**: File deleted successfully.
  ```json
  {
      "message": "File deleted successfully",
      "email": "<user_email>",
      "file_deleted": "<filename>",
      "file_size": <size>,
      "timestamp": "<timestamp>",
      "date": "<date>",
      "updated_deletion_volume": <updated_volume>,
      "total_deletion_count": <count>
  }
  ```
- **400 Bad Request**: Missing filename.
  ```json
  {
      "error": "No filename provided"
  }
  ```
- **401 Unauthorized**: Invalid or missing token.
  ```json
  {
      "error": "Unauthorized"
  }
  ```
- **500 Internal Server Error**: Error during deletion.
  ```json
  {
      "error": "<error_message>"
  }
  ```


### 3. Get Storage Status
**Endpoint:** `/storage-status`  
**Method:** `GET`

**Headers:**
- `Authorization`: `Bearer <user_token>`

**Responses:**
- **200 OK**: Returns storage status.
  ```json
  {
      "total_storage": 52428800,
      "used_storage": 10485760,
      "storage_percentage": 20.0,
      "files": [
          {
              "filename": "username/video.mp4",
              "size": 10485760
          }
      ]
  }
  ```
- **401 Unauthorized**: Invalid or missing token.
  ```json
  {
      "error": "Unauthorized"
  }
  ```
Here is the markdown documentation for the API endpoints:


### 4. Download Video to Client
**Endpoint:** `/download/disk/<filename>`  
**Method:** `GET`

**Headers:**
- `Authorization`: `Bearer <user_token>`

**Path Parameters:**
- `<filename>`: Name of the file to be downloaded.

**Responses:**
- **200 OK**: File downloaded successfully.
  - Returns the requested file as an attachment.
- **401 Unauthorized**: Invalid or missing token.
  ```json
  {
      "error": "Unauthorized"
  }
  ```
- **404 Not Found**: File not found in user's storage.
  ```json
  {
      "error": "File not found in user's storage"
  }
  ```
  ```json
  {
      "error": "User storage not found"
  }
  ```
- **500 Internal Server Error**: Error during download or cleanup.
  ```json
  {
      "error": "<error_message>"
  }
  ```

---

### 5. Stream Video
**Endpoint:** `/stream/video/<filename>`  
**Method:** `GET`

**Headers:**
- `Authorization`: `Bearer <user_token>`

**Path Parameters:**
- `<filename>`: Name of the file to be streamed.

**Responses:**
- **200 OK / 206 Partial Content**: Streams video to the client with range support.
- **401 Unauthorized**: Invalid or missing token.
  ```json
  {
      "error": "Unauthorized"
  }
  ```
- **404 Not Found**: File not found in user's storage or GCS.
  ```json
  {
      "error": "File not found in user's storage"
  }
  ```
  ```json
  {
      "error": "User storage not found"
  }
  ```
- **500 Internal Server Error**: Error during streaming.
  ```json
  {
      "error": "<error_message>"
  }
  ```

---

### 6. Stream Video with Signed URL
**Endpoint:** `/stream/direct/<filename>`  
**Method:** `GET`

**Headers:**
- `Authorization`: `Bearer <user_token>`

**Path Parameters:**
- `<filename>`: Name of the file to be streamed via signed URL.

**Responses:**
- **200 OK**: Returns a signed URL for streaming the video.
  ```json
  {
      "url": "<signed_url>"
  }
  ```
- **401 Unauthorized**: Invalid or missing token.
  ```json
  {
      "error": "Unauthorized"
  }
  ```
- **404 Not Found**: File not found in user's storage or GCS.
  ```json
  {
      "error": "File not found in user's storage"
  }
  ```
  ```json
  {
      "error": "User storage not found"
  }
  ```
- **500 Internal Server Error**: Error generating the signed URL.
  ```json
  {
      "error": "<error_message>"
  }
  ```


## Code Structure
- **`upload_blueprint`**: Handles video uploads.
- **`delete_blueprint`**: Handles video deletions.
- **`status_blueprint`**: Handles storage status retrieval.
- **`download_blueprint`**: Handles video downloads and streams.
- **`UserService`**: Validates user tokens via the User Account Management Service.
- **`GCSService`**: Interfaces with Google Cloud Storage for file operations.
- **`MongoService`**: Manages user storage data in MongoDB.

## Deployment

### Local Development
1. Set up environment variables:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
   export MONGO_URI="mongodb://localhost:27017/"
   export USER_SERVICE_URL="http://user-service-url"
   ```
2. Run the Flask app locally:
   ```bash
   flask run
   ```

### Deployment on GCP
1. Deploy the application using Cloud Run, Compute Engine, or Kubernetes.
2. Assign the appropriate service account to the environment with permissions for:
   - Google Cloud Storage.
   - MongoDB access.
   - User Service token validation.
3. Update the `USER_SERVICE_URL` environment variable to point to the deployed User Service.

## Additional Notes
- **Storage Alerts**: If a user's storage exceeds 80%, an alert is sent.
- **Default Storage**: Each user is initialized with 50MB of storage. Adjust as needed in `mongo_service.initialize_user_storage`.

---
For more details or contributions, please open an issue or submit a pull request.

