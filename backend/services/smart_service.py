"""
Smart Service — Phase 9 Marketplace Intelligence & Recommendation Logic

Provides explainable, data-driven recommendation algorithms and insights:
  1. Related / Similar Product Discovery (weighted scoring on category, title, price, condition)
  2. Popular Products (weighted scoring on wishlists, purchase requests, transactions)
  3. Popular Categories (weighted scoring on listings, wishlists, requests, transactions)
  4. Historical Price Insights (comparable product pricing statistics)
  5. Personalized Recommendations (user category interest signals with cold-start fallback)
"""
import re
from bson.objectid import ObjectId
import backend.db
from backend.models.product import ProductModel
from backend.models.category import CategoryModel
from backend.models.user import UserModel


def _format_product(product, include_seller=True):
    """Safely formats product output and fetches seller info."""
    prod = dict(product)
    prod['_id'] = str(prod['_id'])
    if include_seller and prod.get('seller_id'):
        seller = UserModel.get_by_id(prod['seller_id'])
        if seller:
            prod['seller'] = {
                'id': str(seller['_id']),
                'name': seller.get('name'),
                'department': seller.get('department')
            }
        else:
            prod['seller'] = {'id': prod['seller_id'], 'name': 'Unknown User'}

    if 'seller' in prod:
        prod.pop('seller_id', None)

    return prod


def get_related_products(product_id, limit=10):
    """
    Returns related products for a given product ID based on:
      - Same category (+40 points)
      - Title keyword overlap (+15 points per word, max 45)
      - Price similarity within 30% range (+20 points max)
      - Same condition (+10 points)
    Excludes the target product itself and REMOVED products.
    """
    db = backend.db.get_db()
    target_product = ProductModel.get_by_id(product_id)
    if not target_product or target_product.get('status') == 'REMOVED':
        return None

    target_cat = target_product.get('category_id')
    target_price = float(target_product.get('price', 0))
    target_cond = target_product.get('condition')
    target_title_words = set(w.lower() for w in re.findall(r'\w+', target_product.get('title', '')) if len(w) > 2)

    # Candidates: ACTIVE or RESERVED products excluding target product
    candidates = list(db.products.find({
        '_id': {'$ne': ObjectId(product_id)},
        'status': {'$in': ['ACTIVE', 'RESERVED']}
    }))

    scored = []
    for cand in candidates:
        score = 0.0

        # Category match (+40)
        cand_cat = cand.get('category_id')
        if cand_cat == target_cat:
            score += 40.0

        # Title keyword match (+15 per word, max 45)
        cand_words = set(w.lower() for w in re.findall(r'\w+', cand.get('title', '')) if len(w) > 2)
        overlap = target_title_words.intersection(cand_words)
        if overlap:
            overlap_score = min(len(overlap) * 15.0, 45.0)
            score += overlap_score

        # Price similarity (+20 if within 30% range)
        cand_price = float(cand.get('price', 0))
        if target_price > 0:
            price_diff_pct = abs(cand_price - target_price) / target_price
            if price_diff_pct <= 0.30:
                score += 20.0 * (1.0 - price_diff_pct)

        # Condition match (+10)
        if cand.get('condition') == target_cond:
            score += 10.0

        # Determine explainable reason
        if cand_cat == target_cat and target_price > 0 and abs(cand_price - target_price) / target_price <= 0.30:
            reason = "Same category and similar price range"
        elif cand_cat == target_cat and overlap:
            reason = "Same category and matching title keywords"
        elif cand_cat == target_cat:
            reason = "Same category"
        elif overlap:
            reason = "Matching title keywords"
        else:
            reason = "Similar marketplace item"

        formatted = _format_product(cand)
        scored.append({
            'product': formatted,
            'score': round(score, 1),
            'reason': reason
        })

    scored.sort(key=lambda x: (x['score'], x['product'].get('created_at', '')), reverse=True)
    return scored[:limit]


def get_popular_products(limit=10):
    """
    Returns popular products ranked by marketplace activity:
      popularity_score = (wishlists * 2.0) + (purchase_requests * 3.0) + (completed_txs * 5.0)
    Excludes REMOVED products.
    """
    db = backend.db.get_db()

    wishlist_counts = {}
    for doc in db.wishlist.aggregate([
        {'$group': {'_id': '$product_id', 'count': {'$sum': 1}}}
    ]):
        wishlist_counts[doc['_id']] = doc['count']

    pr_counts = {}
    for doc in db.purchase_requests.aggregate([
        {'$group': {'_id': '$product_id', 'count': {'$sum': 1}}}
    ]):
        pr_counts[doc['_id']] = doc['count']

    tx_counts = {}
    for doc in db.transactions.aggregate([
        {'$match': {'status': 'COMPLETED'}},
        {'$group': {'_id': '$product_id', 'count': {'$sum': 1}}}
    ]):
        tx_counts[doc['_id']] = doc['count']

    products = list(db.products.find({'status': {'$in': ['ACTIVE', 'RESERVED']}}))

    scored = []
    for p in products:
        pid = str(p['_id'])
        w_cnt = wishlist_counts.get(pid, 0)
        pr_cnt = pr_counts.get(pid, 0)
        tx_cnt = tx_counts.get(pid, 0)

        score = (w_cnt * 2.0) + (pr_cnt * 3.0) + (tx_cnt * 5.0)

        if tx_cnt > 0:
            reason = "Highly active in completed sales"
        elif pr_cnt > 0 and w_cnt > 0:
            reason = "Frequently wishlisted and requested by buyers"
        elif w_cnt > 0:
            reason = "Frequently added to student wishlists"
        elif pr_cnt > 0:
            reason = "High buyer interest and purchase requests"
        else:
            reason = "Recently listed marketplace item"

        formatted = _format_product(p)
        scored.append({
            'product': formatted,
            'popularity_score': round(score, 1),
            'reason': reason
        })

    scored.sort(key=lambda x: (x['popularity_score'], str(x['product'].get('created_at', ''))), reverse=True)
    return scored[:limit]


def get_popular_categories(limit=10):
    """
    Returns popular categories ranked by active listings, wishlist adds, requests, and sales:
      demand_score = (active_listings * 1.0) + (wishlists * 2.0) + (requests * 3.0) + (completed_txs * 5.0)
    """
    db = backend.db.get_db()

    product_counts = {}
    for doc in db.products.aggregate([
        {'$match': {'status': {'$in': ['ACTIVE', 'RESERVED']}}},
        {'$group': {'_id': '$category_id', 'count': {'$sum': 1}}}
    ]):
        if doc['_id']:
            product_counts[doc['_id']] = doc['count']

    wishlist_counts = {}
    for doc in db.wishlist.find():
        pid = doc.get('product_id')
        if pid:
            prod = ProductModel.get_by_id(pid)
            if prod and prod.get('category_id'):
                cat_id = prod['category_id']
                wishlist_counts[cat_id] = wishlist_counts.get(cat_id, 0) + 1

    pr_counts = {}
    for doc in db.purchase_requests.find():
        pid = doc.get('product_id')
        if pid:
            prod = ProductModel.get_by_id(pid)
            if prod and prod.get('category_id'):
                cat_id = prod['category_id']
                pr_counts[cat_id] = pr_counts.get(cat_id, 0) + 1

    tx_counts = {}
    for doc in db.transactions.find({'status': 'COMPLETED'}):
        pid = doc.get('product_id')
        if pid:
            prod = ProductModel.get_by_id(pid)
            if prod and prod.get('category_id'):
                cat_id = prod['category_id']
                tx_counts[cat_id] = tx_counts.get(cat_id, 0) + 1

    categories = CategoryModel.get_all_active()
    scored = []
    for cat in categories:
        slug = cat['slug']
        act_cnt = product_counts.get(slug, 0)
        w_cnt = wishlist_counts.get(slug, 0)
        pr_cnt = pr_counts.get(slug, 0)
        tx_cnt = tx_counts.get(slug, 0)

        score = (act_cnt * 1.0) + (w_cnt * 2.0) + (pr_cnt * 3.0) + (tx_cnt * 5.0)

        if tx_cnt > 0:
            reason = "High transaction volume"
        elif pr_cnt > 0:
            reason = "High buyer request volume"
        elif w_cnt > 0:
            reason = "High student wishlist interest"
        else:
            reason = "Active marketplace category"

        scored.append({
            'category': cat,
            'demand_score': round(score, 1),
            'active_listings': act_cnt,
            'reason': reason
        })

    scored.sort(key=lambda x: x['demand_score'], reverse=True)
    return scored[:limit]


def get_price_insights(product_id):
    """
    Returns historical price statistics for a product compared to products in the same category:
      - current_price
      - historical_average
      - min_price
      - max_price
      - comparable_count
      - insufficient_data flag
    """
    db = backend.db.get_db()
    product = ProductModel.get_by_id(product_id)
    if not product or product.get('status') == 'REMOVED':
        return None

    cat_id = product.get('category_id')
    current_price = float(product.get('price', 0))

    # Comparable products in same category (excluding REMOVED)
    comparables = list(db.products.find({
        'category_id': cat_id,
        'status': {'$ne': 'REMOVED'}
    }))

    prices = [float(p['price']) for p in comparables if 'price' in p]

    if len(prices) < 2:
        return {
            'product_id': product_id,
            'current_price': current_price,
            'historical_average': None,
            'min_price': None,
            'max_price': None,
            'comparable_count': len(prices),
            'insufficient_data': True,
            'price_comparison': "Insufficient historical data to calculate price insights"
        }

    avg_price = round(sum(prices) / len(prices), 2)
    min_price = min(prices)
    max_price = max(prices)

    if current_price < avg_price * 0.90:
        comparison = "Priced below historical average"
    elif current_price > avg_price * 1.10:
        comparison = "Priced above historical average"
    else:
        comparison = "Priced fairly at historical market rate"

    return {
        'product_id': product_id,
        'current_price': current_price,
        'historical_average': avg_price,
        'min_price': min_price,
        'max_price': max_price,
        'comparable_count': len(prices),
        'insufficient_data': False,
        'price_comparison': comparison
    }


def get_personalized_recommendations(user_id, limit=10):
    """
    Returns personalized recommendations for an authenticated user based on:
      - Wishlist category interests
      - Purchase request category interests
      - Transaction category interests
    Includes smooth cold-start fallback to popular products if user has no activity.
    Excludes products owned by the user.
    """
    db = backend.db.get_db()

    user_category_interests = {}

    # Wishlist signals
    for doc in db.wishlist.find({'user_id': user_id}):
        pid = doc.get('product_id')
        prod = ProductModel.get_by_id(pid) if pid else None
        if prod and prod.get('category_id'):
            cat = prod['category_id']
            user_category_interests[cat] = user_category_interests.get(cat, 0) + 2

    # Purchase request signals
    for doc in db.purchase_requests.find({'buyer_id': user_id}):
        pid = doc.get('product_id')
        prod = ProductModel.get_by_id(pid) if pid else None
        if prod and prod.get('category_id'):
            cat = prod['category_id']
            user_category_interests[cat] = user_category_interests.get(cat, 0) + 3

    # Transaction signals
    for doc in db.transactions.find({'$or': [{'buyer_id': user_id}, {'seller_id': user_id}]}):
        pid = doc.get('product_id')
        prod = ProductModel.get_by_id(pid) if pid else None
        if prod and prod.get('category_id'):
            cat = prod['category_id']
            user_category_interests[cat] = user_category_interests.get(cat, 0) + 4

    # Fetch active products not owned by the user
    active_products = list(db.products.find({
        'seller_id': {'$ne': user_id},
        'status': 'ACTIVE'
    }))

    if not active_products:
        return []

    # Cold-start fallback if user has no interaction history
    if not user_category_interests:
        popular_items = get_popular_products(limit=limit * 2)
        results = []
        for item in popular_items:
            p = item['product']
            # Exclude user's own products
            p_seller_id = p.get('seller', {}).get('id') or p.get('seller_id')
            if p_seller_id == user_id:
                continue
            results.append({
                'product': p,
                'score': item['popularity_score'],
                'reason': "Popular across campus (cold-start recommendation)"
            })
        return results[:limit]

    # Warm personalization scoring
    scored = []
    for p in active_products:
        pid = str(p['_id'])
        cat_id = p.get('category_id')
        cat_weight = user_category_interests.get(cat_id, 0)

        score = cat_weight * 10.0

        if cat_weight > 0:
            cat_doc = CategoryModel.get_by_slug(cat_id)
            cat_name = cat_doc['name'] if cat_doc else cat_id
            reason = f"Based on your interest in {cat_name}"
        else:
            score = 1.0
            reason = "Recommended marketplace item"

        formatted = _format_product(p)
        scored.append({
            'product': formatted,
            'score': round(score, 1),
            'reason': reason
        })

    scored.sort(key=lambda x: (x['score'], str(x['product'].get('created_at', ''))), reverse=True)
    return scored[:limit]
