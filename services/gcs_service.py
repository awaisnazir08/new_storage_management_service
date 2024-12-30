from google.cloud import storage
from config import CLOUD_PROJECT_ID
from io import BytesIO
import datetime
from google.oauth2 import service_account
class GCSService:
    def __init__(self, bucket_name):
        credentials = service_account.Credentials.from_service_account_file(r'first-scout-444113-h2-b60899a0d7a5.json')
        self.client = storage.Client(project=CLOUD_PROJECT_ID, credentials=credentials)
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, filename, file):
        blob = self.bucket.blob(filename)
        blob.upload_from_file(file)

    def delete_file(self, filename):
        blob = self.bucket.blob(filename)
        blob.delete()

    def get_streaming_blob(self, filename):
        """
        Returns a blob object for streaming if it exists
        """
        blob = self.bucket.get_blob(filename)
        if blob.exists():
            return blob
        return None

    def download_to_disk(self, filename, destination_path):
        """
        Downloads file content from GCS and saves it directly to the given path on disk.
        """
        blob = self.bucket.blob(filename)
        if blob.exists():
            blob.download_to_filename(destination_path)
            return destination_path
        return None

    def generate_download_signed_url_v4(self, blob_name):
        """Generates a v4 signed URL for downloading a blob.

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        """

        blob = self.bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="GET"
        )

        print("Generated GET signed URL:")
        print(url)
        return url
