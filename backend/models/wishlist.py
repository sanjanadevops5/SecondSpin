import datetime
from bson.objectid import ObjectId
import pymongo

class WishlistModel:
    @staticmethod
    def collection():
        import backend.db
        return backend.db.get_db().wishlists

    @staticmethod
    def setup_indexes():
        """Creates the necessary indexes for the wishlists collection."""
        collection = WishlistModel.collection()
        collection.create_index([("user_id", pymongo.ASCENDING), ("product_id", pymongo.ASCENDING)], unique=True)
        collection.create_index("user_id")

    @staticmethod
    def add_item(user_id, product_id):
        """Adds a product to a user's wishlist."""
        doc = {
            'user_id': user_id,
            'product_id': product_id,
            'created_at': datetime.datetime.now(datetime.timezone.utc)
        }
        try:
            result = WishlistModel.collection().insert_one(doc)
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            return None # Already exists

    @staticmethod
    def get_user_wishlist(user_id):
        """Retrieves all wishlist items for a user."""
        items = list(WishlistModel.collection().find({'user_id': user_id}).sort('created_at', -1))
        for item in items:
            item['_id'] = str(item['_id'])
        return items

    @staticmethod
    def remove_item(user_id, product_id):
        """Removes a product from a user's wishlist."""
        result = WishlistModel.collection().delete_one({
            'user_id': user_id,
            'product_id': product_id
        })
        return result.deleted_count > 0
