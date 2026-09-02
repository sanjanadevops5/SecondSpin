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

---

### 1.4 `wishlists`
Stores saved product items for each user. Enables buyers to bookmark listings for later.

- `_id`: ObjectId
- `user_id`: String (matches User `_id` — the owner of the wishlist entry)
- `product_id`: String (matches Product `_id`)
- `created_at`: Datetime UTC

**Relationships:**
- `user_id` references `users._id`. Derived exclusively from the authenticated JWT; the client cannot specify a different user.
- `product_id` references `products._id`.

**Ownership & Security Rules:**
- A user can only read and delete their own wishlist entries. Entries are always scoped to the authenticated user's ID.
- Adding a product with status `SOLD` or `REMOVED` is rejected (HTTP 400). `ACTIVE` and `RESERVED` products may be added.
- Existing wishlist entries are **not** automatically deleted if a product later becomes `SOLD` or `REMOVED`.
- Wishlist responses return a safe, enriched subset of product data (title, price, condition, images, status) — full product documents and internal seller details are not exposed.

**Indexes:**
- `(user_id, product_id)` — **Unique compound index**. Enforces one entry per user per product. Duplicate inserts are caught as `DuplicateKeyError` and returned as HTTP 409.
- `user_id` — Single-field index for efficient retrieval of a user's full wishlist.

---

### 1.5 `purchase_requests`
Stores buyer-initiated purchase requests sent to sellers for a specific product listing.

- `_id`: ObjectId
- `product_id`: String (matches Product `_id`)
- `buyer_id`: String (matches User `_id` — derived from JWT, never client-supplied)
- `seller_id`: String (matches User `_id` — derived from the product record, never client-supplied)
- `message`: String (optional buyer note, max 1000 characters)
- `status`: String (Enum: `PENDING`, `ACCEPTED`, `REJECTED`, `CANCELLED`)
- `created_at`: Datetime UTC
- `updated_at`: Datetime UTC
- `responded_at`: Datetime UTC or `null` (set when status transitions to `ACCEPTED` or `REJECTED`)

**Relationships:**
- `product_id` references `products._id`.
- `buyer_id` references `users._id`. Always set from `g.user_id` (authenticated JWT claim).
- `seller_id` references `users._id`. Always set from `product.seller_id` at request creation time.

**Ownership & Security Rules:**
- A buyer cannot request their own product (`buyer_id == seller_id` is rejected, HTTP 403).
- Only the seller can accept or reject a request.
- Only the buyer can cancel a request.
- Detail view is restricted to the buyer and seller involved in the request.
- The client cannot supply or manipulate `buyer_id`, `seller_id`, or `status` directly.

**Status Lifecycle:**

```
PENDING ──► ACCEPTED  (seller action only)
PENDING ──► REJECTED  (seller action only)
PENDING ──► CANCELLED (buyer action only)
```

Terminal states (`ACCEPTED`, `REJECTED`, `CANCELLED`) cannot transition to any other status.

**Duplicate Request Rule:**
- Only one `PENDING` request is allowed per `(buyer_id, product_id)` pair at any time.
- A buyer with a `REJECTED` or `CANCELLED` historical request **may** submit a new request. Only active `PENDING` requests are checked.
- Duplicate `PENDING` inserts are rejected with HTTP 409.

**Phase Boundary (Phase 6):**
- Accepting a request does **not** mark the product as `RESERVED` or `SOLD`, and does **not** create a transaction. Transaction and reservation logic belongs to Phase 7.

**Indexes:**
- `(buyer_id, status)` — Compound index for efficiently fetching a buyer's requests by status.
- `(seller_id, status)` — Compound index for efficiently fetching a seller's incoming requests by status.
- `(product_id, status)` — Compound index for checking active requests on a product.
