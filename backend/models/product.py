import datetime
from bson.objectid import ObjectId


class ProductModel:
    CONDITIONS = ['NEW', 'LIKE_NEW', 'GOOD', 'FAIR', 'POOR']
    STATUSES = ['ACTIVE', 'RESERVED', 'SOLD', 'REMOVED']

    @staticmethod
    def collection():
        import backend.db
        return backend.db.get_db().products

    @staticmethod
    def setup_indexes():
        """Creates the necessary indexes for the products collection."""
        collection = ProductModel.collection()
        collection.create_index("seller_id")
        collection.create_index("category_id")
        collection.create_index("status")
        collection.create_index("price")
        collection.create_index("created_at")
        # Text index for search
        collection.create_index([("title", "text"), ("description", "text")])

    @staticmethod
    def create_product(seller_id, category_id, title, description, price, condition, images, attributes):
        """Creates a new product listing."""
        product_doc = {
            'seller_id': seller_id,
            'category_id': category_id,
            'title': title.strip(),
            'description': description.strip(),
            'price': float(price),
            'condition': condition,
            'images': images or [],
            'attributes': attributes or {},
            'status': 'ACTIVE',
            'created_at': datetime.datetime.now(datetime.timezone.utc),
            'updated_at': datetime.datetime.now(datetime.timezone.utc)
        }
        
        result = ProductModel.collection().insert_one(product_doc)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(product_id):
        """Retrieve a product by its ID."""
        try:
            product = ProductModel.collection().find_one({'_id': ObjectId(product_id)})
            if product:
                product['_id'] = str(product['_id'])
            return product
        except Exception:
            return None

    @staticmethod
    def get_by_seller(seller_id):
        """Retrieve all products for a specific seller (excluding REMOVED if needed, but usually seller wants to see all)."""
        products = list(ProductModel.collection().find({'seller_id': seller_id, 'status': {'$ne': 'REMOVED'}}).sort('created_at', -1))
        for p in products:
            p['_id'] = str(p['_id'])
        return products

    @staticmethod
    def update_product(product_id, updates):
        """Update a product (only specific allowed fields)."""
        try:
            updates['updated_at'] = datetime.datetime.now(datetime.timezone.utc)
            result = ProductModel.collection().update_one(
                {'_id': ObjectId(product_id)},
                {'$set': updates}
            )
            return result.modified_count > 0
        except Exception:
            return False

    @staticmethod
    def search_products(query_filters=None, search_text=None, sort_by='newest', page=1, limit=20):
        """
        Search, filter, and paginate products.
        Only returns ACTIVE or RESERVED products for public discovery.
        (Requirement: SOLD remains available for historical reference? Wait, the prompt said ACTIVE are publicly discoverable, RESERVED are visible but unavailable, SOLD remain available for historical/reference, REMOVED must not appear).
        """
        filters = query_filters or {}
        
        # Base filter: Exclude REMOVED by default unless specified
        if 'status' not in filters:
            filters['status'] = {'$in': ['ACTIVE', 'RESERVED', 'SOLD']}
            
        if search_text:
            filters['$text'] = {'$search': search_text}
            
        # Determine sort order
        sort_config = [('created_at', -1)] # default newest
        if sort_by == 'oldest':
            sort_config = [('created_at', 1)]
        elif sort_by == 'price_low_to_high':
            sort_config = [('price', 1)]
        elif sort_by == 'price_high_to_low':
            sort_config = [('price', -1)]
            
        collection = ProductModel.collection()
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch items
        try:
            cursor = collection.find(filters).sort(sort_config).skip(skip).limit(limit)
            items = list(cursor)
            total = collection.count_documents(filters)
        except NotImplementedError:
            # Fallback for mongomock which doesn't support $text
            if '$text' in filters:
                search_text = filters['$text']['$search']
                del filters['$text']
                filters['$or'] = [
                    {'title': {'$regex': search_text, '$options': 'i'}},
                    {'description': {'$regex': search_text, '$options': 'i'}}
                ]
                cursor = collection.find(filters).sort(sort_config).skip(skip).limit(limit)
                items = list(cursor)
                total = collection.count_documents(filters)
            else:
                raise

        
        for p in items:
            p['_id'] = str(p['_id'])
            
        return {
            'items': items,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit if total > 0 else 1
            }
        }
