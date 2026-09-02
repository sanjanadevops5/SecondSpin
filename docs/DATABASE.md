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

---

### 1.6 `transactions`
Records the physical exchange lifecycle that follows an accepted purchase request. Transactions drive the product reservation and sale state changes.

- `_id`: ObjectId
- `purchase_request_id`: String — References `purchase_requests._id`. Unique index prevents duplicate transactions per accepted request.
- `product_id`: String — References `products._id`.
- `buyer_id`: String — References `users._id`. Always derived from the accepted purchase request; never client-supplied.
- `seller_id`: String — References `users._id`. Always derived from the accepted purchase request; never client-supplied.
- `status`: String (Enum: `PENDING`, `RESERVED`, `COMPLETED`, `CANCELLED`)
- `created_at`: Datetime UTC
- `updated_at`: Datetime UTC
- `completed_at`: Datetime UTC or `null`
- `cancelled_at`: Datetime UTC or `null`

**Relationships:**
- `purchase_request_id` references `purchase_requests._id`.
- `product_id` references `products._id`.
- `buyer_id` and `seller_id` both reference `users._id`. Both are derived server-side from the accepted purchase request.

**Ownership & Security Rules:**
- Only the buyer of the accepted purchase request may create a transaction.
- Only the seller may advance the transaction to `RESERVED` or `COMPLETED`.
- Either the buyer or the seller may cancel (`PENDING` or `RESERVED` only).
- Neither the buyer nor the seller can view or modify another user's transaction.
- Client cannot supply or override `buyer_id`, `seller_id`, `product_id`, or `status`.

**Status Lifecycle:**
```
PENDING  ──► RESERVED   (seller confirms meeting arranged)
PENDING  ──► CANCELLED  (buyer or seller)
RESERVED ──► COMPLETED  (seller confirms exchange happened)
RESERVED ──► CANCELLED  (buyer or seller)
COMPLETED ── (terminal — no further transitions)
CANCELLED ── (terminal — no further transitions)
```

**Product State Integration:**
- Transaction created (PENDING): Product → `RESERVED` (atomic conditional update — only if currently `ACTIVE`)
- Transaction → `COMPLETED`: Product → `SOLD`
- Transaction → `CANCELLED`: Product → `ACTIVE` (conditional — only if still `RESERVED`)

**Data Integrity Note (Phase 7):**
- MongoDB does not support multi-document ACID transactions in this implementation. The product reservation is handled via a conditional update (`find_one_and_update` with status filter) which provides strong single-document atomicity. The two-step (insert transaction + update product) is defensible for an academic-scale campus marketplace.

**Indexes:**
- `purchase_request_id` — **Unique index**. One transaction per accepted purchase request.
- `(buyer_id, status)` — Compound index for buyer history queries.
- `(seller_id, status)` — Compound index for seller history queries.
- `(product_id, status)` — Compound index for active-transaction existence checks.

---

### 1.7 `reviews`
Stores post-transaction reviews written by one participant about the other. Tied exclusively to `COMPLETED` transactions to ensure only real exchanges are reviewed.

- `_id`: ObjectId
- `transaction_id`: String — References `transactions._id`.
- `reviewer_id`: String — References `users._id`. Always derived from the authenticated JWT; never client-supplied.
- `reviewee_id`: String — References `users._id`. Must be the other party of the transaction.
- `product_id`: String — References `products._id`. Derived server-side from the transaction; never client-supplied.
- `rating`: Integer (1–5 inclusive)
- `comment`: String (optional, max 1000 characters)
- `created_at`: Datetime UTC

**Relationships:**
- `transaction_id` references `transactions._id`.
- `reviewer_id` and `reviewee_id` both reference `users._id`.
- `product_id` references `products._id`.

**Eligibility Rules:**
- Transaction must exist and be `COMPLETED`.
- Reviewer must be the buyer or seller of that transaction.
- Reviewer cannot review themselves (`reviewer_id != reviewee_id`).
- Reviewee must be the other participant (not a third party).
- Each direction (buyer→seller, seller→buyer) may produce exactly one review per transaction.

**Rating Validation:**
- Must be an integer (Python `int`), not a float, string, boolean, or null.
- Must be in the range 1–5 inclusive.

**Reviews are immutable in Phase 7** — no editing or deletion endpoints are implemented.

**Indexes:**
- `(transaction_id, reviewer_id, reviewee_id)` — **Unique compound index**. Enforces the one-review-per-reviewer-reviewee-per-transaction rule.
- `product_id` — For fetching all reviews related to a product listing.
- `reviewee_id` — For fetching a user's received reviews (trust/seller profile).
- `reviewer_id` — For fetching all reviews authored by a user.

---

### 1.8 `reports` (Phase 8)
Stores user and listing moderation reports for trust & safety administration.

- `_id`: ObjectId
- `reporter_id`: String — References `users._id`. Always derived from JWT authentication.
- `target_type`: String (Enum: `PRODUCT`, `USER`)
- `target_id`: String — References `products._id` or `users._id` depending on `target_type`.
- `reason`: String — Short category reason for report (max 100 characters).
- `description`: String — Optional detailed description (max 1000 characters).
- `status`: String (Enum: `OPEN`, `REVIEWING`, `RESOLVED`, `DISMISSED`)
- `created_at`: Datetime UTC
- `updated_at`: Datetime UTC
- `resolved_at`: Datetime UTC or `null`
- `resolved_by`: String or `null` — References `users._id` of resolving admin.

**Status Lifecycle:**
```
OPEN ──► REVIEWING ──► RESOLVED
OPEN ──► RESOLVED
OPEN ──► DISMISSED
REVIEWING ──► DISMISSED
```

**Indexes:**
- `(reporter_id, status)` — Compound index for fetching reporter's reports.
- `(target_type, target_id)` — Compound index for querying reports per target.
- `status` — Index for filtering open/reviewing reports.
- `created_at` — Index for temporal sorting.


