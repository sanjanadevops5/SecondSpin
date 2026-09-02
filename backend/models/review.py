import datetime
from bson.objectid import ObjectId
import pymongo


class ReviewModel:
    MAX_COMMENT_LENGTH = 1000

    @staticmethod
    def collection():
        import backend.db
        return backend.db.get_db().reviews

    @staticmethod
    def setup_indexes():
        """Creates the necessary indexes for the reviews collection."""
        collection = ReviewModel.collection()
        # One review per reviewer/reviewee pair per transaction
        collection.create_index(
            [
                ('transaction_id', pymongo.ASCENDING),
                ('reviewer_id', pymongo.ASCENDING),
                ('reviewee_id', pymongo.ASCENDING),
            ],
            unique=True,
        )
        # For fetching all reviews about a product (product page)
        collection.create_index('product_id')
        # For fetching all reviews received by a user (seller profile / trust score)
        collection.create_index('reviewee_id')
        # For fetching all reviews written by a user
        collection.create_index('reviewer_id')

    @staticmethod
    def create_review(transaction_id, reviewer_id, reviewee_id, product_id, rating, comment=''):
        """
        Inserts a new review document.
        Returns the new review ID string, or None on DuplicateKeyError
        (same reviewer → reviewee relationship for this transaction already exists).
        """
        doc = {
            'transaction_id': transaction_id,
            'reviewer_id': reviewer_id,
            'reviewee_id': reviewee_id,
            'product_id': product_id,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.datetime.now(datetime.timezone.utc),
        }
        try:
            result = ReviewModel.collection().insert_one(doc)
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            return None

    @staticmethod
    def get_by_id(review_id):
        """Retrieves a single review by its string ID."""
        try:
            review = ReviewModel.collection().find_one({'_id': ObjectId(review_id)})
            if review:
                review['_id'] = str(review['_id'])
            return review
        except Exception:
            return None

    @staticmethod
    def get_by_product(product_id):
        """Retrieves all reviews associated with a product."""
        reviews = list(
            ReviewModel.collection().find({'product_id': product_id}).sort('created_at', -1)
        )
        for r in reviews:
            r['_id'] = str(r['_id'])
        return reviews

    @staticmethod
    def get_by_reviewee(user_id):
        """Retrieves all reviews received by a user (for trust/seller profile)."""
        reviews = list(
            ReviewModel.collection().find({'reviewee_id': user_id}).sort('created_at', -1)
        )
        for r in reviews:
            r['_id'] = str(r['_id'])
        return reviews
