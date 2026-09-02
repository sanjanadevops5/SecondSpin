from flask import Blueprint, request, g
from backend.responses import success_response, error_response
from backend.validation import validate_json
from backend.auth_middleware import jwt_required
from backend.models.wishlist import WishlistModel
from backend.models.product import ProductModel

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/', methods=['POST'])
@jwt_required
@validate_json(required_fields=['product_id'])
def add_to_wishlist():
    """Adds a product to the user's wishlist."""
    data = request.get_json()
    product_id = data['product_id']
    
    product = ProductModel.get_by_id(product_id)
    if not product:
        return error_response(code="NOT_FOUND", message="Product not found.", status_code=404)
        
    if product.get('status') in ['SOLD', 'REMOVED']:
        return error_response(code="UNAVAILABLE", message="This product is no longer available to add to wishlist.", status_code=400)
        
    result = WishlistModel.add_item(g.user_id, product_id)
    if result is None:
        return error_response(code="DUPLICATE_ITEM", message="Product is already in your wishlist.", status_code=409)
        
    return success_response(data={'wishlist_id': result, 'message': 'Product added to wishlist.'}, status_code=201)

@wishlist_bp.route('/', methods=['GET'])
@jwt_required
def get_wishlist():
    """Retrieves the user's wishlist."""
    items = WishlistModel.get_user_wishlist(g.user_id)
    
    enriched_items = []
    for item in items:
        product = ProductModel.get_by_id(item['product_id'])
        # Only return if product exists and is not REMOVED
        if product and product.get('status') != 'REMOVED':
            # Remove sensitive seller_id from public response if needed, 
            # but since wishlist includes products, we can format it.
            # Using _format_product from products if we can, or just basic mapping here.
            item['product'] = {
                'id': str(product['_id']),
                'title': product.get('title'),
                'price': product.get('price'),
                'condition': product.get('condition'),
                'images': product.get('images'),
                'status': product.get('status')
            }
            enriched_items.append(item)
            
    return success_response(data={'items': enriched_items})

@wishlist_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required
def remove_from_wishlist(product_id):
    """Removes a product from the user's wishlist."""
    success = WishlistModel.remove_item(g.user_id, product_id)
    if not success:
        return error_response(code="NOT_FOUND", message="Item not found in your wishlist.", status_code=404)
        
    return success_response(message="Product removed from wishlist.")
