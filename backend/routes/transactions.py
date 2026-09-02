"""
Transactions Blueprint — Phase 7
Handles the transaction lifecycle from creation through completion/cancellation.

Lifecycle:
  PENDING  ──► RESERVED   (seller confirms meeting arranged)
  PENDING  ──► CANCELLED  (buyer or seller)
  RESERVED ──► COMPLETED  (seller confirms exchange happened)
  RESERVED ──► CANCELLED  (buyer or seller)
  COMPLETED ── (terminal)
  CANCELLED ── (terminal)

Product state changes driven by transactions:
  On create  → product becomes RESERVED  (conditional atomic update)
  COMPLETED  → product becomes SOLD
  CANCELLED  → product returns to ACTIVE  (conditional: only if still RESERVED)
"""
import datetime
from flask import Blueprint, request, g

from backend.responses import success_response, error_response
from backend.validation import validate_json
from backend.auth_middleware import jwt_required
from backend.models.transaction import TransactionModel
from backend.models.purchase_request import PurchaseRequestModel
from backend.models.product import ProductModel

transactions_bp = Blueprint('transactions', __name__)


# ---------------------------------------------------------------------------
# POST /api/v1/transactions/
# ---------------------------------------------------------------------------
@transactions_bp.route('/', methods=['POST'])
@jwt_required
@validate_json(required_fields=['purchase_request_id'])
def create_transaction():
    """
    Create a transaction from an ACCEPTED purchase request.
    Only the buyer of the accepted purchase request may create a transaction.

    On success:
      - Transaction is created with status PENDING.
      - Product is atomically moved from ACTIVE → RESERVED.
    """
    data = request.get_json()
    pr_id = data.get('purchase_request_id', '').strip()

    # --- Fetch and validate the purchase request ---
    pr = PurchaseRequestModel.get_by_id(pr_id)
    if not pr:
        return error_response(
            code='NOT_FOUND',
            message='Purchase request not found.',
            status_code=404,
        )

    # Only the buyer of the PR may initiate the transaction
    if pr['buyer_id'] != g.user_id:
        return error_response(
            code='FORBIDDEN',
            message='Only the buyer of this purchase request can create a transaction.',
            status_code=403,
        )

    # PR must be in ACCEPTED state
    if pr['status'] != 'ACCEPTED':
        return error_response(
            code='INVALID_STATE',
            message='A transaction can only be created from an ACCEPTED purchase request.',
            status_code=400,
        )

    product_id = pr['product_id']
    buyer_id   = pr['buyer_id']
    seller_id  = pr['seller_id']

    # --- Fetch and validate the product ---
    product = ProductModel.get_by_id(product_id)
    if not product:
        return error_response(
            code='NOT_FOUND',
            message='Product not found.',
            status_code=404,
        )

    if product['status'] in ['SOLD', 'REMOVED']:
        return error_response(
            code='UNAVAILABLE',
            message='Product is no longer available for a transaction.',
            status_code=400,
        )

    # --- Prevent double-reservation ---
    if TransactionModel.has_active_transaction(product_id):
        return error_response(
            code='CONFLICT',
            message='An active transaction already exists for this product.',
            status_code=409,
        )

    # --- Create the transaction (unique index on purchase_request_id) ---
    txn_id = TransactionModel.create_transaction(pr_id, product_id, buyer_id, seller_id)
    if txn_id is None:
        return error_response(
            code='DUPLICATE_TRANSACTION',
            message='A transaction already exists for this purchase request.',
            status_code=409,
        )

    # --- Atomically reserve the product ---
    # Conditional update: only succeeds if product is still ACTIVE.
    # If it fails, the transaction we just created is cancelled to avoid orphaned state.
    reserved = ProductModel.try_reserve(product_id)
    if not reserved:
        TransactionModel.update_status(txn_id, 'CANCELLED')
        return error_response(
            code='CONFLICT',
            message='Product is no longer available for reservation.',
            status_code=409,
        )

    return success_response(
        data={
            'transaction_id': txn_id,
            'message': 'Transaction created. Product is now RESERVED.',
        },
        status_code=201,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/transactions/mine
# ---------------------------------------------------------------------------
@transactions_bp.route('/mine', methods=['GET'])
@jwt_required
def get_buyer_transactions():
    """Returns all transactions initiated by the authenticated buyer."""
    txns = TransactionModel.get_by_buyer(g.user_id)
    return success_response(data={'items': txns})


# ---------------------------------------------------------------------------
# GET /api/v1/transactions/received
# ---------------------------------------------------------------------------
@transactions_bp.route('/received', methods=['GET'])
@jwt_required
def get_seller_transactions():
    """Returns all transactions involving the authenticated seller's products."""
    txns = TransactionModel.get_by_seller(g.user_id)
    return success_response(data={'items': txns})


# ---------------------------------------------------------------------------
# GET /api/v1/transactions/<transaction_id>
# ---------------------------------------------------------------------------
@transactions_bp.route('/<transaction_id>', methods=['GET'])
@jwt_required
def get_transaction(transaction_id):
    """
    Returns the full detail of a transaction.
    Only the buyer or seller of this transaction may view it.
    """
    txn = TransactionModel.get_by_id(transaction_id)
    if not txn:
        return error_response(
            code='NOT_FOUND',
            message='Transaction not found.',
            status_code=404,
        )

    if g.user_id not in (txn['buyer_id'], txn['seller_id']):
        return error_response(
            code='FORBIDDEN',
            message='You are not authorized to view this transaction.',
            status_code=403,
        )

    return success_response(data=txn)


# ---------------------------------------------------------------------------
# PATCH /api/v1/transactions/<transaction_id>/reserve
# ---------------------------------------------------------------------------
@transactions_bp.route('/<transaction_id>/reserve', methods=['PATCH'])
@jwt_required
def reserve_transaction(transaction_id):
    """
    Seller confirms the meeting is arranged: PENDING → RESERVED.
    Product remains RESERVED at the product level.
    Only the seller may call this endpoint.
    """
    txn = TransactionModel.get_by_id(transaction_id)
    if not txn:
        return error_response(
            code='NOT_FOUND',
            message='Transaction not found.',
            status_code=404,
        )

    if txn['seller_id'] != g.user_id:
        return error_response(
            code='FORBIDDEN',
            message='Only the seller can confirm the reservation.',
            status_code=403,
        )

    if not TransactionModel.is_valid_transition(txn['status'], 'RESERVED'):
        return error_response(
            code='INVALID_TRANSITION',
            message=f"Cannot transition from {txn['status']} to RESERVED.",
            status_code=400,
        )

    TransactionModel.update_status(transaction_id, 'RESERVED')
    return success_response(message='Transaction is now RESERVED.')


# ---------------------------------------------------------------------------
# PATCH /api/v1/transactions/<transaction_id>/complete
# ---------------------------------------------------------------------------
@transactions_bp.route('/<transaction_id>/complete', methods=['PATCH'])
@jwt_required
def complete_transaction(transaction_id):
    """
    Seller marks the exchange as complete: RESERVED → COMPLETED.
    Product transitions from RESERVED → SOLD.
    Only the seller may call this endpoint.
    """
    txn = TransactionModel.get_by_id(transaction_id)
    if not txn:
        return error_response(
            code='NOT_FOUND',
            message='Transaction not found.',
            status_code=404,
        )

    if txn['seller_id'] != g.user_id:
        return error_response(
            code='FORBIDDEN',
            message='Only the seller can complete a transaction.',
            status_code=403,
        )

    if not TransactionModel.is_valid_transition(txn['status'], 'COMPLETED'):
        return error_response(
            code='INVALID_TRANSITION',
            message=f"Cannot transition from {txn['status']} to COMPLETED.",
            status_code=400,
        )

    success = TransactionModel.update_status(transaction_id, 'COMPLETED')
    if not success:
        return error_response(
            code='DATABASE_ERROR',
            message='Failed to complete transaction.',
            status_code=500,
        )

    # Transition product to SOLD
    ProductModel.update_product(txn['product_id'], {'status': 'SOLD'})

    return success_response(message='Transaction completed. Product is now SOLD.')


# ---------------------------------------------------------------------------
# PATCH /api/v1/transactions/<transaction_id>/cancel
# ---------------------------------------------------------------------------
@transactions_bp.route('/<transaction_id>/cancel', methods=['PATCH'])
@jwt_required
def cancel_transaction(transaction_id):
    """
    Cancels a PENDING or RESERVED transaction.
    Either the buyer or the seller may cancel.
    Product is returned to ACTIVE status (conditional: only if currently RESERVED).
    """
    txn = TransactionModel.get_by_id(transaction_id)
    if not txn:
        return error_response(
            code='NOT_FOUND',
            message='Transaction not found.',
            status_code=404,
        )

    if g.user_id not in (txn['buyer_id'], txn['seller_id']):
        return error_response(
            code='FORBIDDEN',
            message='Only the buyer or seller can cancel this transaction.',
            status_code=403,
        )

    if not TransactionModel.is_valid_transition(txn['status'], 'CANCELLED'):
        return error_response(
            code='INVALID_TRANSITION',
            message=f"Cannot cancel a transaction with status {txn['status']}.",
            status_code=400,
        )

    success = TransactionModel.update_status(transaction_id, 'CANCELLED')
    if not success:
        return error_response(
            code='DATABASE_ERROR',
            message='Failed to cancel transaction.',
            status_code=500,
        )

    # Restore product to ACTIVE — only if it is still RESERVED.
    # (Guards against accidental un-selling a SOLD product.)
    ProductModel.collection().update_one(
        {'_id': __import__('bson').ObjectId(txn['product_id']), 'status': 'RESERVED'},
        {'$set': {
            'status': 'ACTIVE',
            'updated_at': datetime.datetime.now(datetime.timezone.utc),
        }},
    )

    return success_response(message='Transaction cancelled. Product is now ACTIVE.')
