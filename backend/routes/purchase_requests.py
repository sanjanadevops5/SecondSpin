from flask import Blueprint, request, g
from backend.responses import success_response, error_response
from backend.validation import validate_json
from backend.auth_middleware import jwt_required
from backend.models.purchase_request import PurchaseRequestModel
from backend.models.product import ProductModel

purchase_requests_bp = Blueprint('purchase_requests', __name__)

@purchase_requests_bp.route('/', methods=['POST'])
@jwt_required
@validate_json(required_fields=['product_id'])
def create_request():
    """Create a new purchase request."""
    data = request.get_json()
    product_id = data['product_id']
    message = data.get('message', '').strip()
    
    if len(message) > 1000:
        return error_response(code="INVALID_MESSAGE", message="Message cannot exceed 1000 characters.", status_code=400)
        
    product = ProductModel.get_by_id(product_id)
    if not product:
        return error_response(code="NOT_FOUND", message="Product not found.", status_code=404)
        
    if product.get('status') != 'ACTIVE':
        return error_response(code="UNAVAILABLE", message="This product is no longer active.", status_code=400)
        
    if product['seller_id'] == g.user_id:
        return error_response(code="FORBIDDEN", message="You cannot request your own product.", status_code=403)
        
    if PurchaseRequestModel.has_active_request(g.user_id, product_id):
        return error_response(code="DUPLICATE_REQUEST", message="You already have a pending request for this product.", status_code=409)
        
    req_id = PurchaseRequestModel.create_request(product_id, g.user_id, product['seller_id'], message)
    return success_response(data={'request_id': req_id, 'message': 'Purchase request sent.'}, status_code=201)

@purchase_requests_bp.route('/mine', methods=['GET'])
@jwt_required
def get_my_requests():
    """Get buyer's outgoing requests."""
    requests = PurchaseRequestModel.get_by_buyer(g.user_id)
    return success_response(data={'items': requests})

@purchase_requests_bp.route('/received', methods=['GET'])
@jwt_required
def get_received_requests():
    """Get seller's incoming requests."""
    requests = PurchaseRequestModel.get_by_seller(g.user_id)
    return success_response(data={'items': requests})

@purchase_requests_bp.route('/<request_id>', methods=['GET'])
@jwt_required
def get_request_detail(request_id):
    """View details of a specific request."""
    req = PurchaseRequestModel.get_by_id(request_id)
    if not req:
        return error_response(code="NOT_FOUND", message="Request not found.", status_code=404)
        
    if req['buyer_id'] != g.user_id and req['seller_id'] != g.user_id:
        return error_response(code="FORBIDDEN", message="You do not have permission to view this request.", status_code=403)
        
    return success_response(data=req)

@purchase_requests_bp.route('/<request_id>/accept', methods=['PATCH'])
@jwt_required
def accept_request(request_id):
    """Seller accepts the request."""
    req = PurchaseRequestModel.get_by_id(request_id)
    if not req:
        return error_response(code="NOT_FOUND", message="Request not found.", status_code=404)
        
    if req['seller_id'] != g.user_id:
        return error_response(code="FORBIDDEN", message="Only the seller can accept this request.", status_code=403)
        
    if req['status'] != 'PENDING':
        return error_response(code="INVALID_TRANSITION", message=f"Cannot accept a request that is currently {req['status']}.", status_code=400)
        
    # Check if product is still ACTIVE
    product = ProductModel.get_by_id(req['product_id'])
    if not product or product.get('status') != 'ACTIVE':
        return error_response(code="UNAVAILABLE", message="Product is no longer active.", status_code=400)
        
    # Update request to ACCEPTED
    success = PurchaseRequestModel.update_status(request_id, 'ACCEPTED')
    if success:
        return success_response(message="Request accepted.")
        
    return error_response(code="DATABASE_ERROR", message="Failed to accept request.", status_code=500)

@purchase_requests_bp.route('/<request_id>/reject', methods=['PATCH'])
@jwt_required
def reject_request(request_id):
    """Seller rejects the request."""
    req = PurchaseRequestModel.get_by_id(request_id)
    if not req:
        return error_response(code="NOT_FOUND", message="Request not found.", status_code=404)
        
    if req['seller_id'] != g.user_id:
        return error_response(code="FORBIDDEN", message="Only the seller can reject this request.", status_code=403)
        
    if req['status'] != 'PENDING':
        return error_response(code="INVALID_TRANSITION", message=f"Cannot reject a request that is currently {req['status']}.", status_code=400)
        
    success = PurchaseRequestModel.update_status(request_id, 'REJECTED')
    if success:
        return success_response(message="Request rejected.")
        
    return error_response(code="DATABASE_ERROR", message="Failed to reject request.", status_code=500)

@purchase_requests_bp.route('/<request_id>/cancel', methods=['PATCH'])
@jwt_required
def cancel_request(request_id):
    """Buyer cancels the request."""
    req = PurchaseRequestModel.get_by_id(request_id)
    if not req:
        return error_response(code="NOT_FOUND", message="Request not found.", status_code=404)
        
    if req['buyer_id'] != g.user_id:
        return error_response(code="FORBIDDEN", message="Only the buyer can cancel this request.", status_code=403)
        
    if req['status'] != 'PENDING':
        return error_response(code="INVALID_TRANSITION", message=f"Cannot cancel a request that is currently {req['status']}.", status_code=400)
        
    success = PurchaseRequestModel.update_status(request_id, 'CANCELLED')
    if success:
        return success_response(message="Request cancelled.")
        
    return error_response(code="DATABASE_ERROR", message="Failed to cancel request.", status_code=500)
