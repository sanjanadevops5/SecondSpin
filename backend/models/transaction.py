import datetime
from bson.objectid import ObjectId
import pymongo


class TransactionModel:
    STATUSES = ['PENDING', 'RESERVED', 'COMPLETED', 'CANCELLED']

    # Valid status transitions enforced at the model level
    VALID_TRANSITIONS = {
        'PENDING': ['RESERVED', 'CANCELLED'],
        'RESERVED': ['COMPLETED', 'CANCELLED'],
        'COMPLETED': [],
        'CANCELLED': [],
    }

    @staticmethod
    def collection():
        import backend.db
        return backend.db.get_db().transactions

    @staticmethod
    def setup_indexes():
        """Creates the necessary indexes for the transactions collection."""
        collection = TransactionModel.collection()
        # One transaction per accepted purchase request (hard uniqueness guarantee)
        collection.create_index('purchase_request_id', unique=True)
        # Buyer and seller history with status filtering
        collection.create_index([('buyer_id', pymongo.ASCENDING), ('status', pymongo.ASCENDING)])
        collection.create_index([('seller_id', pymongo.ASCENDING), ('status', pymongo.ASCENDING)])
        # Active-transaction check per product
        collection.create_index([('product_id', pymongo.ASCENDING), ('status', pymongo.ASCENDING)])

    @staticmethod
    def has_active_transaction(product_id):
        """Returns True if a PENDING or RESERVED transaction already exists for this product."""
        count = TransactionModel.collection().count_documents({
            'product_id': product_id,
            'status': {'$in': ['PENDING', 'RESERVED']}
        })
        return count > 0

    @staticmethod
    def create_transaction(purchase_request_id, product_id, buyer_id, seller_id):
        """
        Inserts a new transaction document with status PENDING.
        Returns the new transaction ID string, or None on DuplicateKeyError
        (i.e. a transaction for this purchase_request_id already exists).
        """
        doc = {
            'purchase_request_id': purchase_request_id,
            'product_id': product_id,
            'buyer_id': buyer_id,
            'seller_id': seller_id,
            'status': 'PENDING',
            'created_at': datetime.datetime.now(datetime.timezone.utc),
            'updated_at': datetime.datetime.now(datetime.timezone.utc),
            'completed_at': None,
            'cancelled_at': None,
        }
        try:
            result = TransactionModel.collection().insert_one(doc)
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            return None

    @staticmethod
    def get_by_id(transaction_id):
        """Retrieves a single transaction by its string ID."""
        try:
            txn = TransactionModel.collection().find_one({'_id': ObjectId(transaction_id)})
            if txn:
                txn['_id'] = str(txn['_id'])
            return txn
        except Exception:
            return None

    @staticmethod
    def get_by_buyer(buyer_id):
        """Retrieves all transactions initiated by a buyer."""
        txns = list(
            TransactionModel.collection().find({'buyer_id': buyer_id}).sort('created_at', -1)
        )
        for t in txns:
            t['_id'] = str(t['_id'])
        return txns

    @staticmethod
    def get_by_seller(seller_id):
        """Retrieves all transactions involving a seller's products."""
        txns = list(
            TransactionModel.collection().find({'seller_id': seller_id}).sort('created_at', -1)
        )
        for t in txns:
            t['_id'] = str(t['_id'])
        return txns

    @staticmethod
    def is_valid_transition(current_status, new_status):
        """Returns True if the status transition is allowed."""
        return new_status in TransactionModel.VALID_TRANSITIONS.get(current_status, [])

    @staticmethod
    def update_status(transaction_id, new_status):
        """
        Updates the transaction status and relevant timestamps.
        Returns True if the document was modified.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        updates = {
            'status': new_status,
            'updated_at': now,
        }
        if new_status == 'COMPLETED':
            updates['completed_at'] = now
        elif new_status == 'CANCELLED':
            updates['cancelled_at'] = now

        result = TransactionModel.collection().update_one(
            {'_id': ObjectId(transaction_id)},
            {'$set': updates}
        )
        return result.modified_count > 0
