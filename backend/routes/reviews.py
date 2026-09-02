"""
Reviews Blueprint — Phase 7
Handles review creation and retrieval tied to completed transactions.

Eligibility rules:
  - Transaction must exist and be COMPLETED.
  - Reviewer must be the buyer or seller of that transaction.
  - Reviewer cannot review themselves.
  - Reviewee must be the other party of the transaction.
  - Only one review per reviewer → reviewee relationship per transaction.

Rating: Integer 1–5 only. Booleans are rejected.
Comment: Optional string, max 1000 characters.
Reviews are immutable after creation in Phase 7.
"""
from flask import Blueprint, request, g

from backend.responses import success_response, error_response
from backend.validation import validate_json
from backend.auth_middleware import jwt_required
from backend.models.review import ReviewModel
from backend.models.transaction import TransactionModel

reviews_bp = Blueprint('reviews', __name__)

MAX_COMMENT_LENGTH = ReviewModel.MAX_COMMENT_LENGTH


def _validate_rating(rating):
    """
    Returns True only for integers 1–5, explicitly excluding booleans.
    JSON `true`/`false` parse to Python bool which is a subclass of int —
    those are rejected here.
    """
    if isinstance(rating, bool):
        return False
    if not isinstance(rating, int):
        return False
    return 1 <= rating <= 5


# ---------------------------------------------------------------------------
# POST /api/v1/reviews/
# ---------------------------------------------------------------------------
@reviews_bp.route('/', methods=['POST'])
@jwt_required
@validate_json(required_fields=['transaction_id', 'reviewee_id', 'rating'])
def create_review():
    """
    Create a review for a completed transaction.

    Body:
      transaction_id: str    — ID of the COMPLETED transaction
      reviewee_id:    str    — ID of the user being reviewed (must be the other party)
      rating:         int    — 1–5 (integers only)
      comment:        str    — optional, max 1000 chars

    Server derives: reviewer_id (from JWT), product_id (from transaction).
    """
    data = request.get_json()
    transaction_id = data.get('transaction_id', '').strip()
    reviewee_id    = data.get('reviewee_id', '').strip()
    rating         = data.get('rating')
    comment        = data.get('comment', '')

    # --- Fetch transaction ---
    txn = TransactionModel.get_by_id(transaction_id)
    if not txn:
        return error_response(
            code='NOT_FOUND',
            message='Transaction not found.',
            status_code=404,
        )

    # --- Transaction must be COMPLETED ---
    if txn['status'] != 'COMPLETED':
        return error_response(
            code='NOT_ELIGIBLE',
            message='Reviews can only be submitted for COMPLETED transactions.',
            status_code=400,
        )

    reviewer_id = g.user_id

    # --- Reviewer must be a participant ---
    if reviewer_id not in (txn['buyer_id'], txn['seller_id']):
        return error_response(
            code='FORBIDDEN',
            message='You did not participate in this transaction.',
            status_code=403,
        )

    # --- No self-review ---
    if reviewer_id == reviewee_id:
        return error_response(
            code='SELF_REVIEW',
            message='You cannot review yourself.',
            status_code=400,
        )

    # --- Reviewee must be the other party ---
    other_party = txn['seller_id'] if reviewer_id == txn['buyer_id'] else txn['buyer_id']
    if reviewee_id != other_party:
        return error_response(
            code='INVALID_REVIEWEE',
            message='Reviewee must be the other participant in this transaction.',
            status_code=403,
        )

    # --- Validate rating ---
    if not _validate_rating(rating):
        return error_response(
            code='INVALID_RATING',
            message='Rating must be an integer between 1 and 5.',
            status_code=400,
        )

    # --- Validate comment ---
    if not isinstance(comment, str):
        return error_response(
            code='INVALID_COMMENT',
            message='Comment must be a string.',
            status_code=400,
        )
    if len(comment) > MAX_COMMENT_LENGTH:
        return error_response(
            code='COMMENT_TOO_LONG',
            message=f'Comment must be at most {MAX_COMMENT_LENGTH} characters.',
            status_code=400,
        )

    # --- Derive product_id from the transaction (never from client) ---
    product_id = txn['product_id']

    # --- Create the review (unique index enforces one-per-relationship) ---
    review_id = ReviewModel.create_review(
        transaction_id=transaction_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
        product_id=product_id,
        rating=rating,
        comment=comment,
    )
    if review_id is None:
        return error_response(
            code='DUPLICATE_REVIEW',
            message='You have already submitted a review for this transaction.',
            status_code=409,
        )

    return success_response(
        data={'review_id': review_id, 'message': 'Review submitted successfully.'},
        status_code=201,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/reviews/product/<product_id>
# ---------------------------------------------------------------------------
@reviews_bp.route('/product/<product_id>', methods=['GET'])
@jwt_required
def get_reviews_by_product(product_id):
    """Returns all reviews associated with a product."""
    reviews = ReviewModel.get_by_product(product_id)
    return success_response(data={'items': reviews})


# ---------------------------------------------------------------------------
# GET /api/v1/reviews/user/<user_id>
# ---------------------------------------------------------------------------
@reviews_bp.route('/user/<user_id>', methods=['GET'])
@jwt_required
def get_reviews_by_user(user_id):
    """Returns all reviews received by a user (their trust/reputation profile)."""
    reviews = ReviewModel.get_by_reviewee(user_id)
    return success_response(data={'items': reviews})


# ---------------------------------------------------------------------------
# GET /api/v1/reviews/<review_id>
# ---------------------------------------------------------------------------
@reviews_bp.route('/<review_id>', methods=['GET'])
@jwt_required
def get_review(review_id):
    """Returns the full detail of a single review."""
    review = ReviewModel.get_by_id(review_id)
    if not review:
        return error_response(
            code='NOT_FOUND',
            message='Review not found.',
            status_code=404,
        )
    return success_response(data=review)
