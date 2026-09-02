import datetime
from bson.objectid import ObjectId
import pymongo

class PurchaseRequestModel:
    STATUSES = ['PENDING', 'ACCEPTED', 'REJECTED', 'CANCELLED']

    @staticmethod
    def collection():
        import backend.db
        return backend.db.get_db().purchase_requests

    @staticmethod
    def setup_indexes():
        """Creates the necessary indexes for the purchase requests collection."""
        collection = PurchaseRequestModel.collection()
        collection.create_index([("buyer_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)])
        collection.create_index([("seller_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)])
        collection.create_index([("product_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)])

    @staticmethod
    def has_active_request(buyer_id, product_id):
        """Checks if a buyer already has a PENDING request for this product."""
        count = PurchaseRequestModel.collection().count_documents({
            'buyer_id': buyer_id,
            'product_id': product_id,
            'status': 'PENDING'
        })
        return count > 0

    @staticmethod
    def create_request(product_id, buyer_id, seller_id, message=""):
        """Creates a new purchase request."""
        doc = {
            'product_id': product_id,
            'buyer_id': buyer_id,
            'seller_id': seller_id,
            'message': message,
            'status': 'PENDING',
            'created_at': datetime.datetime.now(datetime.timezone.utc),
            'updated_at': datetime.datetime.now(datetime.timezone.utc),
            'responded_at': None
        }
        result = PurchaseRequestModel.collection().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(request_id):
        """Retrieves a single request by ID."""
        try:
            req = PurchaseRequestModel.collection().find_one({'_id': ObjectId(request_id)})
            if req:
                req['_id'] = str(req['_id'])
            return req
        except Exception:
            return None

    @staticmethod
    def get_by_buyer(buyer_id):
        """Retrieves all requests made by a buyer."""
        requests = list(PurchaseRequestModel.collection().find({'buyer_id': buyer_id}).sort('created_at', -1))
        for req in requests:
            req['_id'] = str(req['_id'])
        return requests

    @staticmethod
    def get_by_seller(seller_id):
        """Retrieves all requests received by a seller."""
        requests = list(PurchaseRequestModel.collection().find({'seller_id': seller_id}).sort('created_at', -1))
        for req in requests:
            req['_id'] = str(req['_id'])
        return requests

    @staticmethod
    def update_status(request_id, new_status):
        """Updates the status of a request."""
        updates = {
            'status': new_status,
            'updated_at': datetime.datetime.now(datetime.timezone.utc)
        }
        if new_status in ['ACCEPTED', 'REJECTED']:
            updates['responded_at'] = datetime.datetime.now(datetime.timezone.utc)
            
        result = PurchaseRequestModel.collection().update_one(
            {'_id': ObjectId(request_id)},
            {'$set': updates}
        )
        return result.modified_count > 0
