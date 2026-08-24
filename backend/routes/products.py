from flask import Blueprint, request, g
from backend.responses import success_response, error_response
from backend.validation import validate_json
from backend.auth_middleware import jwt_required
from backend.models.product import ProductModel
from backend.models.category import CategoryModel
from backend.models.user import UserModel
import re

products_bp = Blueprint('products', __name__)

def _format_product(product, include_seller=True):
    # Formats product output and safely fetches seller info
    if include_seller and product.get('seller_id'):
        seller = UserModel.get_by_id(product['seller_id'])
        if seller:
            product['seller'] = {
                'id': str(seller['_id']),
                'name': seller.get('name'),
                'department': seller.get('department')
            }
        else:
            product['seller'] = {'id': product['seller_id'], 'name': 'Unknown User'}
    
    # Do not expose internal raw seller_id at root if nested seller exists
    if 'seller' in product:
        product.pop('seller_id', None)
        
    return product

@products_bp.route('/', methods=['GET'])
def get_products():
    """Public discovery endpoint with pagination, search, and filtering."""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        if page < 1: page = 1
        if limit < 1: limit = 20
        if limit > 100: limit = 100 # Maximum page size
    except ValueError:
        return error_response(code="INVALID_PAGINATION", message="Page and limit must be positive integers.", status_code=400)

    search_text = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'newest')
    
    if sort_by not in ['newest', 'oldest', 'price_low_to_high', 'price_high_to_low']:
        return error_response(code="INVALID_SORT", message="Invalid sort parameter.", status_code=400)

    filters = {}
    
    # Category Filter
    category = request.args.get('category')
    if category:
        filters['category_id'] = category
        
    # Condition Filter
    condition = request.args.get('condition')
    if condition:
        if condition not in ProductModel.CONDITIONS:
            return error_response(code="INVALID_CONDITION", message="Invalid condition filter.", status_code=400)
        filters['condition'] = condition
        
    # Price Filter
    try:
        min_price = request.args.get('min_price')
        if min_price is not None:
            filters.setdefault('price', {})['$gte'] = float(min_price)
            
        max_price = request.args.get('max_price')
        if max_price is not None:
            filters.setdefault('price', {})['$lte'] = float(max_price)
    except ValueError:
        return error_response(code="INVALID_PRICE_FILTER", message="Price filters must be numbers.", status_code=400)
        
    # Status Filter
    status = request.args.get('status')
    if status:
        if status not in ProductModel.STATUSES or status == 'REMOVED':
            # Do not allow searching for REMOVED via public API
            return error_response(code="INVALID_STATUS", message="Invalid or unauthorized status filter.", status_code=400)
        filters['status'] = status
    
    try:
        result = ProductModel.search_products(filters, search_text, sort_by, page, limit)
        
        # Enrich products with safe seller info
        formatted_items = [_format_product(item) for item in result['items']]
        result['items'] = formatted_items
        
        return success_response(data=result)
    except Exception as e:
        return error_response(code="DATABASE_ERROR", message="Failed to retrieve products.", status_code=500)

@products_bp.route('/me', methods=['GET'])
@jwt_required
def get_my_products():
    """Retrieve all listings owned by the authenticated seller."""
    try:
        products = ProductModel.get_by_seller(g.user_id)
        # Note: We can optionally include seller object or not since they know who they are.
        formatted_items = [_format_product(item, include_seller=False) for item in products]
        return success_response(data={'items': formatted_items})
    except Exception as e:
        return error_response(code="DATABASE_ERROR", message="Failed to retrieve your products.", status_code=500)

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Retrieve a single product by ID."""
    product = ProductModel.get_by_id(product_id)
    if not product:
        return error_response(code="NOT_FOUND", message="Product not found.", status_code=404)
        
    if product.get('status') == 'REMOVED':
        return error_response(code="NOT_FOUND", message="Product has been removed.", status_code=404)
        
    return success_response(data=_format_product(product))

def _validate_image_url(url):
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None

@products_bp.route('/', methods=['POST'])
@jwt_required
@validate_json(required_fields=['title', 'description', 'price', 'category_id', 'condition'])
def create_product():
    """Create a new product listing."""
    data = request.get_json()
    
    title = data['title'].strip()
    description = data['description'].strip()
    
    if not title or len(title) > 100:
        return error_response(code="INVALID_TITLE", message="Title must be between 1 and 100 characters.", status_code=400)
        
    if not description or len(description) > 2000:
        return error_response(code="INVALID_DESCRIPTION", message="Description must be between 1 and 2000 characters.", status_code=400)
        
    try:
        price = float(data['price'])
        if price < 0:
            raise ValueError
    except (ValueError, TypeError):
        return error_response(code="INVALID_PRICE", message="Price must be a valid positive number.", status_code=400)
        
    category_id = data['category_id']
    if not CategoryModel.is_valid(category_id):
        return error_response(code="INVALID_CATEGORY", message="Invalid or inactive category.", status_code=400)
        
    condition = data['condition']
    if condition not in ProductModel.CONDITIONS:
        return error_response(code="INVALID_CONDITION", message=f"Condition must be one of: {', '.join(ProductModel.CONDITIONS)}", status_code=400)
        
    images = data.get('images', [])
    if not isinstance(images, list):
        return error_response(code="INVALID_IMAGES", message="Images must be an array of URLs.", status_code=400)
    if len(images) > 5:
        return error_response(code="TOO_MANY_IMAGES", message="Maximum of 5 images allowed.", status_code=400)
    for url in images:
        if not _validate_image_url(url):
            return error_response(code="INVALID_IMAGE_URL", message=f"Invalid image URL: {url}", status_code=400)
            
    attributes = data.get('attributes', {})
    if not isinstance(attributes, dict):
        return error_response(code="INVALID_ATTRIBUTES", message="Attributes must be an object.", status_code=400)

    # Server enforced seller ID
    seller_id = g.user_id
    
    try:
        product_id = ProductModel.create_product(seller_id, category_id, title, description, price, condition, images, attributes)
        return success_response(data={'product_id': product_id, 'message': 'Product created successfully.'}, status_code=201)
    except Exception as e:
        return error_response(code="DATABASE_ERROR", message="Failed to create product.", status_code=500)

@products_bp.route('/<product_id>', methods=['PUT'])
@jwt_required
def update_product(product_id):
    """Edit an existing listing (owner only)."""
    product = ProductModel.get_by_id(product_id)
    if not product or product.get('status') == 'REMOVED':
        return error_response(code="NOT_FOUND", message="Product not found.", status_code=404)
        
    if product['seller_id'] != g.user_id:
        return error_response(code="FORBIDDEN", message="You do not have permission to modify this product.", status_code=403)
        
    data = request.get_json() or {}
    updates = {}
    
    # Status Transition
    if 'status' in data:
        new_status = data['status']
        if new_status not in ProductModel.STATUSES:
            return error_response(code="INVALID_STATUS", message=f"Status must be one of: {', '.join(ProductModel.STATUSES)}", status_code=400)
        
        # Valid Transitions Logic
        current_status = product['status']
        # For MVP, allow any transition among ACTIVE, RESERVED, SOLD except moving out of SOLD/REMOVED if we want strictness, 
        # but the prompt says: "ACTIVE -> RESERVED, ACTIVE -> SOLD, ACTIVE -> REMOVED. Prevent nonsensical transitions."
        # If it's SOLD or REMOVED, it shouldn't go back to ACTIVE.
        if current_status in ['SOLD', 'REMOVED'] and new_status not in ['SOLD', 'REMOVED']:
             return error_response(code="INVALID_TRANSITION", message=f"Cannot transition from {current_status} to {new_status}.", status_code=400)
             
        updates['status'] = new_status
        
    # Safe editable fields
    if 'title' in data:
        title = data['title'].strip()
        if not title or len(title) > 100:
             return error_response(code="INVALID_TITLE", message="Title must be between 1 and 100 characters.", status_code=400)
        updates['title'] = title
        
    if 'description' in data:
        description = data['description'].strip()
        if not description or len(description) > 2000:
             return error_response(code="INVALID_DESCRIPTION", message="Description must be between 1 and 2000 characters.", status_code=400)
        updates['description'] = description
        
    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0: raise ValueError
            updates['price'] = price
        except (ValueError, TypeError):
             return error_response(code="INVALID_PRICE", message="Price must be a valid positive number.", status_code=400)
             
    if 'condition' in data:
        condition = data['condition']
        if condition not in ProductModel.CONDITIONS:
            return error_response(code="INVALID_CONDITION", message="Invalid condition.", status_code=400)
        updates['condition'] = condition
        
    if 'category_id' in data:
        category_id = data['category_id']
        if not CategoryModel.is_valid(category_id):
            return error_response(code="INVALID_CATEGORY", message="Invalid or inactive category.", status_code=400)
        updates['category_id'] = category_id
        
    if 'images' in data:
        images = data['images']
        if not isinstance(images, list) or len(images) > 5:
             return error_response(code="INVALID_IMAGES", message="Maximum of 5 images allowed.", status_code=400)
        for url in images:
            if not _validate_image_url(url):
                return error_response(code="INVALID_IMAGE_URL", message=f"Invalid image URL: {url}", status_code=400)
        updates['images'] = images
        
    if 'attributes' in data:
        if not isinstance(data['attributes'], dict):
             return error_response(code="INVALID_ATTRIBUTES", message="Attributes must be an object.", status_code=400)
        updates['attributes'] = data['attributes']

    if not updates:
        return success_response(message="No fields to update.")
        
    success = ProductModel.update_product(product_id, updates)
    if not success:
        return error_response(code="DATABASE_ERROR", message="Failed to update product.", status_code=500)
        
    return success_response(message="Product updated successfully.")

@products_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required
def delete_product(product_id):
    """Soft delete a listing (owner only). Transitions status to REMOVED."""
    product = ProductModel.get_by_id(product_id)
    if not product:
        return error_response(code="NOT_FOUND", message="Product not found.", status_code=404)
        
    if product['seller_id'] != g.user_id:
        return error_response(code="FORBIDDEN", message="You do not have permission to delete this product.", status_code=403)
        
    if product['status'] == 'REMOVED':
        return success_response(message="Product is already removed.")
        
    success = ProductModel.update_product(product_id, {'status': 'REMOVED'})
    if not success:
        return error_response(code="DATABASE_ERROR", message="Failed to remove product.", status_code=500)
        
    return success_response(message="Product successfully removed.")
