# SecondSpin Database Schema & Indexes

## 1. Collections

### 1.1 `users`
Stores user credentials, profile information, and roles.
- `_id`: ObjectId
- `name`: String
- `email`: String (Unique)
- `password_hash`: String
- `role`: String (e.g., 'student', 'admin')
- `department`: String
- `verification_status`: String (e.g., 'VERIFIED', 'UNVERIFIED')
- `account_status`: String (e.g., 'ACTIVE', 'SUSPENDED')
- `profile`: Object
- `created_at`: Datetime UTC
- `updated_at`: Datetime UTC

**Indexes:**
- `email` (Unique)

### 1.2 `categories`
Stores product categories. Seeded via `scripts/seed_categories.py`.
- `_id`: ObjectId
- `name`: String
- `slug`: String (Unique, used as `category_id` in products)
- `is_active`: Boolean
- `created_at`: Datetime UTC
- `updated_at`: Datetime UTC

**Indexes:**
- `slug` (Unique)

### 1.3 `products`
Stores marketplace listings.
- `_id`: ObjectId
- `seller_id`: String (matches User `_id`)
- `category_id`: String (matches Category `slug`)
- `title`: String
- `description`: String
- `price`: Float
- `condition`: String (Enum: `NEW`, `LIKE_NEW`, `GOOD`, `FAIR`, `POOR`)
- `images`: Array of Strings (URLs)
- `attributes`: Object (Key-value pairs for specific category traits)
- `status`: String (Enum: `ACTIVE`, `RESERVED`, `SOLD`, `REMOVED`)
- `created_at`: Datetime UTC
- `updated_at`: Datetime UTC

**Indexes:**
- `seller_id`: For fetching a user's own listings.
- `category_id`: For category filtering.
- `status`: For filtering out removed items.
- `price`: For price range filtering and sorting.
- `created_at`: For chronological sorting.
- `title_text_description_text`: Compound Text Index for marketplace search.

## 2. Product Lifecycle & Status Transitions
The product status field controls visibility and lifecycle:
- `ACTIVE`: Publicly discoverable in marketplace search.
- `RESERVED`: Kept visible (e.g. for historical view or direct links) but indicates pending sale.
- `SOLD`: Remains for transaction history and reference, but generally filtered out of primary "available" views unless specifically requested.
- `REMOVED`: Soft-deleted. Removed listings must not appear in normal public discovery.

## 3. Marketplace Discovery (Search & Filter)
- **Pagination:** Uses `skip` and `limit`. Defaults to `page=1`, `limit=20`. Maximum limit is 100.
- **Filtering:** Filters are applied directly to the MongoDB query object (e.g., `{'status': 'ACTIVE', 'category_id': 'textbooks'}`).
- **Search:** Uses MongoDB `$text` search against the `title` and `description` fields.
- **Sorting:** Translates client-friendly strings (e.g., `price_low_to_high`) to MongoDB sort directives (`[('price', 1)]`).
