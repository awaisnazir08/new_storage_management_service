import pymongo

class MongoService:
    def __init__(self, uri):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client['user_management']
        self.storage_collection = self.db['video_storage']
        self.storage_collection.create_index('email', unique=True)

    def find_user_storage(self, email):
        return self.storage_collection.find_one({'email': email})

    def initialize_user_storage(self, email, total_storage):
        storage = {
            'email': email,
            'total_storage': total_storage,
            'used_storage': 0,
            'files': []
        }
        self.storage_collection.insert_one(storage)
        return storage

    def update_storage(self, email, update_data):
        self.storage_collection.update_one({'email': email}, update_data)
