# SecondSpin API Guide

## 1. Overview
The SecondSpin API is a RESTful, JSON-based web service that serves both the SecondSpin Web Application and the Flutter Mobile Application. It acts as the single source of truth and data access layer, sitting between the clients and the MongoDB Atlas database.

## 2. Base URL
All API requests in production will go to the configured domain. 
The current base prefix for all endpoints is: `/api/v1`

## 3. Versioning
We use URI versioning. The current version is `v1`.
All new endpoints must be placed under `/api/v1`.

## 4. Authentication
Authentication is **implemented** as part of Phase 4. Endpoints require JWT authentication tokens passed in the `Authorization: Bearer <token>` header.

## 5. Request Format
- All requests containing a payload must set the `Content-Type: application/json` header.
- Data must be structured as valid JSON.

## 6. Response Format
Successful responses follow a predictable envelope structure:
```json
{
  "success": true,
  "message": "Optional success message",
  "data": {
    "key": "value"
  }
}
```

## 7. Error Format
Errors follow a consistent structure. Stack traces and sensitive details are never exposed to the client.
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

## 8. HTTP Status Codes
- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `204 No Content`: Request succeeded, no body returned.
- `400 Bad Request`: Malformed JSON or invalid parameters.
- `401 Unauthorized`: Authentication required or failed.
- `403 Forbidden`: Authenticated, but lacking permissions.
- `404 Not Found`: Resource or route does not exist.
- `409 Conflict`: Resource state conflict (e.g., duplicate user).
- `422 Unprocessable Entity`: Validation failure on fields.
- `500 Internal Server Error`: Unexpected server issue.

## 9. CORS
Cross-Origin Resource Sharing is enabled for configured origins via the `CORS_ORIGINS` environment variable. In development, it defaults to allowing all origins (`*`).

## 10. Health Endpoint
**Implemented**
- **GET** `/api/v1/health`
- **Purpose**: Checks the application status and environment.

## 11. Validation Strategy
We use a lightweight `@validate_json` decorator to assert required fields and basic type checking on incoming payloads before they hit route logic. This keeps controllers clean and predictable.

## 12. Implemented Endpoints

### Infrastructure
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Application health check |

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a new student account |
| POST | `/api/v1/auth/login` | Login and receive a JWT |

### Users
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/users/me` | Get own profile |
| PATCH | `/api/v1/users/me` | Update own profile fields |

### Categories
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/categories` | List all active product categories |

### Products
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/products/` | Create a new product listing |
| GET | `/api/v1/products/` | Search, filter, and paginate marketplace listings |
| GET | `/api/v1/products/me` | Get the authenticated user's own listings |
| GET | `/api/v1/products/<id>` | Get a single product by ID |
| PATCH | `/api/v1/products/<id>` | Update own product listing |
| DELETE | `/api/v1/products/<id>` | Remove own product listing (soft-delete to REMOVED) |

---

### Wishlist — `/api/v1/wishlist`
All endpoints require `Authorization: Bearer <token>`.

---

#### `POST /api/v1/wishlist/`
Adds a product to the authenticated user's wishlist.

**Auth:** Required (any authenticated user)

**Request Body:**
```json
{ "product_id": "<string>" }
```

**Success (201):**
```json
{ "success": true, "data": { "wishlist_id": "<string>", "message": "Product added to wishlist." } }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 | Product not found |
| 400 `UNAVAILABLE` | Product status is `SOLD` or `REMOVED` |
| 409 `DUPLICATE_ITEM` | Product already in wishlist |
| 422 | Missing `product_id` field |

**Business Rules:**
- `user_id` is always derived from the JWT — the client cannot specify another user.
- `ACTIVE` and `RESERVED` products may be wishlisted; `SOLD` and `REMOVED` are rejected.

---

#### `GET /api/v1/wishlist/`
Returns the authenticated user's wishlist, enriched with live product data. Products with status `REMOVED` are silently excluded from the response.

**Auth:** Required

**Success (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "_id": "<wishlist_entry_id>",
        "user_id": "<string>",
        "product_id": "<string>",
        "created_at": "<datetime>",
        "product": {
          "id": "<string>",
          "title": "<string>",
          "price": "<number>",
          "condition": "<string>",
          "images": ["<url>"],
          "status": "<string>"
        }
      }
    ]
  }
}
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |

---

#### `DELETE /api/v1/wishlist/<product_id>`
Removes a product from the authenticated user's wishlist.

**Auth:** Required

**URL Parameter:** `product_id` — the product's ID string.

**Success (200):**
```json
{ "success": true, "message": "Product removed from wishlist." }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 | Item not found in this user's wishlist |

**Business Rules:**
- Scoped to the authenticated user — a user cannot remove another user's wishlist entry.

---

### Purchase Requests — `/api/v1/purchase-requests`
All endpoints require `Authorization: Bearer <token>`.

---

#### `POST /api/v1/purchase-requests/`
Creates a new purchase request from a buyer to a seller for a specific product.

**Auth:** Required (buyer role — any authenticated user who is not the product seller)

**Request Body:**
```json
{ "product_id": "<string>", "message": "<optional string, max 1000 chars>" }
```

**Success (201):**
```json
{ "success": true, "data": { "request_id": "<string>", "message": "Purchase request sent." } }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 | Product not found |
| 400 `UNAVAILABLE` | Product is not `ACTIVE` (is `SOLD`, `RESERVED`, or `REMOVED`) |
| 403 `FORBIDDEN` | Buyer is the product's seller (self-purchase blocked) |
| 409 `DUPLICATE_REQUEST` | Buyer already has a `PENDING` request for this product |
| 400 `INVALID_MESSAGE` | Message exceeds 1000 characters |
| 422 | Missing `product_id` field |

**Business Rules:**
- `buyer_id` is derived from JWT; `seller_id` is derived from the product record — neither can be client-supplied.
- Status is always initialized as `PENDING`.
- Only one active `PENDING` request per buyer/product pair is allowed. A buyer with a prior `REJECTED` or `CANCELLED` request **may** create a new one.

---

#### `GET /api/v1/purchase-requests/mine`
Returns all purchase requests made by the authenticated buyer.

**Auth:** Required

**Success (200):**
```json
{ "success": true, "data": { "items": [ { ...request fields... } ] } }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |

---

#### `GET /api/v1/purchase-requests/received`
Returns all purchase requests received by the authenticated seller (i.e., requests for products owned by this user).

**Auth:** Required

**Success (200):**
```json
{ "success": true, "data": { "items": [ { ...request fields... } ] } }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |

---

#### `GET /api/v1/purchase-requests/<request_id>`
Returns the full detail of a single purchase request.

**Auth:** Required (must be the buyer or the seller of this request)

**URL Parameter:** `request_id` — the request's ID string.

**Success (200):**
```json
{
  "success": true,
  "data": {
    "_id": "<string>",
    "product_id": "<string>",
    "buyer_id": "<string>",
    "seller_id": "<string>",
    "message": "<string>",
    "status": "PENDING | ACCEPTED | REJECTED | CANCELLED",
    "created_at": "<datetime>",
    "updated_at": "<datetime>",
    "responded_at": "<datetime | null>"
  }
}
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 | Request not found |
| 403 | Authenticated user is neither the buyer nor the seller |

---

#### `PATCH /api/v1/purchase-requests/<request_id>/accept`
Seller accepts a `PENDING` purchase request.

**Auth:** Required (must be the seller of this request)

**Success (200):**
```json
{ "success": true, "message": "Request accepted." }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 | Request not found |
| 403 | Authenticated user is not the seller |
| 400 `INVALID_TRANSITION` | Request is not in `PENDING` status |
| 400 `UNAVAILABLE` | Product is no longer `ACTIVE` |
| 500 | Database update failed |

**Business Rules (Phase 6):**
- Only `PENDING` → `ACCEPTED` is a valid transition.
- The product's status remains `ACTIVE` after acceptance — reservation and transaction logic is handled in Phase 7.
- Accepting does not modify other open requests for the same product.

---

#### `PATCH /api/v1/purchase-requests/<request_id>/reject`
Seller rejects a `PENDING` purchase request.

**Auth:** Required (must be the seller of this request)

**Success (200):**
```json
{ "success": true, "message": "Request rejected." }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 | Request not found |
| 403 | Authenticated user is not the seller |
| 400 `INVALID_TRANSITION` | Request is not in `PENDING` status |
| 500 | Database update failed |

**Business Rules:**
- Only `PENDING` → `REJECTED` is a valid transition.
- A buyer whose request is `REJECTED` may submit a new request for the same product.

---

#### `PATCH /api/v1/purchase-requests/<request_id>/cancel`
Buyer cancels their own `PENDING` purchase request.

**Auth:** Required (must be the buyer of this request)

**Success (200):**
```json
{ "success": true, "message": "Request cancelled." }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 | Request not found |
| 403 | Authenticated user is not the buyer |
| 400 `INVALID_TRANSITION` | Request is not in `PENDING` status |
| 500 | Database update failed |

**Business Rules:**
- Only `PENDING` → `CANCELLED` is a valid transition.
- A buyer whose request is `CANCELLED` may submit a new request for the same product.


---

## 13. Transactions — `/api/v1/transactions`
All endpoints require `Authorization: Bearer <token>`.

The transaction lifecycle (and corresponding product states) is:
```
PENDING  ──► RESERVED   (seller action)  → product stays RESERVED
PENDING  ──► CANCELLED  (buyer or seller) → product → ACTIVE
RESERVED ──► COMPLETED  (seller action)  → product → SOLD
RESERVED ──► CANCELLED  (buyer or seller) → product → ACTIVE
```

---

#### `POST /api/v1/transactions/`
Creates a transaction from an ACCEPTED purchase request. Only the buyer of the PR may call this.

**Auth:** Required (must be the buyer of the purchase request)

**Request Body:**
```json
{ "purchase_request_id": "<string>" }
```

**Success (201):**
```json
{ "success": true, "data": { "transaction_id": "<string>", "message": "Transaction created. Product is now RESERVED." } }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 `NOT_FOUND` | Purchase request not found |
| 403 `FORBIDDEN` | Caller is not the buyer of the purchase request |
| 400 `INVALID_STATE` | Purchase request is not in ACCEPTED status |
| 404 `NOT_FOUND` | Product not found |
| 400 `UNAVAILABLE` | Product is SOLD or REMOVED |
| 409 `CONFLICT` | Active transaction already exists for this product |
| 409 `DUPLICATE_TRANSACTION` | Transaction already exists for this purchase request |
| 422 | Missing `purchase_request_id` |

**Business Rules:**
- `buyer_id` and `seller_id` are derived from the purchase request — never client-supplied.
- Product must be ACTIVE at creation time; atomically moves to RESERVED.
- If product reservation fails (race condition), the created transaction is auto-cancelled.

---

#### `GET /api/v1/transactions/mine`
Returns all transactions initiated by the authenticated buyer.

**Auth:** Required

**Success (200):** `{ "success": true, "data": { "items": [ { ...transaction fields... } ] } }`

---

#### `GET /api/v1/transactions/received`
Returns all transactions involving the authenticated seller's products.

**Auth:** Required

**Success (200):** `{ "success": true, "data": { "items": [ { ...transaction fields... } ] } }`

---

#### `GET /api/v1/transactions/<transaction_id>`
Returns full detail of a single transaction. Only the buyer or seller may view it.

**Auth:** Required

**Success (200):**
```json
{
  "success": true,
  "data": {
    "_id": "<string>",
    "purchase_request_id": "<string>",
    "product_id": "<string>",
    "buyer_id": "<string>",
    "seller_id": "<string>",
    "status": "PENDING | RESERVED | COMPLETED | CANCELLED",
    "created_at": "<datetime>",
    "updated_at": "<datetime>",
    "completed_at": "<datetime | null>",
    "cancelled_at": "<datetime | null>"
  }
}
```

**Error Responses:** 401 | 404 `NOT_FOUND` | 403 `FORBIDDEN`

---

#### `PATCH /api/v1/transactions/<id>/reserve`
Seller confirms meeting arranged: `PENDING → RESERVED`.

**Auth:** Required (seller only)

**Success (200):** `{ "success": true, "message": "Transaction is now RESERVED." }`

**Error Responses:** 401 | 404 | 403 | 400 `INVALID_TRANSITION`

---

#### `PATCH /api/v1/transactions/<id>/complete`
Seller confirms exchange happened: `RESERVED → COMPLETED`. Product becomes `SOLD`.

**Auth:** Required (seller only)

**Success (200):** `{ "success": true, "message": "Transaction completed. Product is now SOLD." }`

**Error Responses:** 401 | 404 | 403 | 400 `INVALID_TRANSITION`

---

#### `PATCH /api/v1/transactions/<id>/cancel`
Cancels a `PENDING` or `RESERVED` transaction. Either buyer or seller may cancel. Product returns to `ACTIVE`.

**Auth:** Required (buyer or seller)

**Success (200):** `{ "success": true, "message": "Transaction cancelled. Product is now ACTIVE." }`

**Error Responses:** 401 | 404 | 403 | 400 `INVALID_TRANSITION`

---

## 14. Reviews — `/api/v1/reviews`
All endpoints require `Authorization: Bearer <token>`.

Reviews are immutable after creation in Phase 7.

---

#### `POST /api/v1/reviews/`
Submits a review for a completed transaction. Reviewer must be a participant; reviewee must be the other party.

**Auth:** Required

**Request Body:**
```json
{
  "transaction_id": "<string>",
  "reviewee_id":    "<string>",
  "rating":         4,
  "comment":        "<optional string, max 1000 chars>"
}
```

**Success (201):**
```json
{ "success": true, "data": { "review_id": "<string>", "message": "Review submitted successfully." } }
```

**Error Responses:**
| Code | Reason |
|---|---|
| 401 | Missing or invalid JWT |
| 404 `NOT_FOUND` | Transaction not found |
| 400 `NOT_ELIGIBLE` | Transaction is not COMPLETED |
| 403 `FORBIDDEN` | Caller is not a participant in this transaction |
| 400 `SELF_REVIEW` | Reviewer and reviewee are the same user |
| 403 `INVALID_REVIEWEE` | Reviewee is not the other participant |
| 400 `INVALID_RATING` | Rating is not an integer 1–5 (booleans, decimals, strings rejected) |
| 400 `INVALID_COMMENT` | Comment is not a string |
| 400 `COMMENT_TOO_LONG` | Comment exceeds 1000 characters |
| 409 `DUPLICATE_REVIEW` | This reviewer has already reviewed this reviewee for this transaction |
| 422 | Missing required fields |

**Business Rules:**
- `reviewer_id` is always derived from JWT — never from the request body.
- `product_id` is always derived from the transaction — never from the request body.
- Buyer may review Seller; Seller may review Buyer. Both directions are independent.
- Rating must be a JSON integer (not `true`/`false`, not `4.5`, not `"5"`).

---

#### `GET /api/v1/reviews/product/<product_id>`
Returns all reviews associated with a product listing.

**Auth:** Required

**Success (200):** `{ "success": true, "data": { "items": [ { ...review fields... } ] } }`

---

#### `GET /api/v1/reviews/user/<user_id>`
Returns all reviews received by a user (seller trust profile).

**Auth:** Required

**Success (200):** `{ "success": true, "data": { "items": [ { ...review fields... } ] } }`

---

#### `GET /api/v1/reviews/<review_id>`
Returns the full detail of a single review.

**Auth:** Required

**Success (200):**
```json
{
  "success": true,
  "data": {
    "_id": "<string>",
    "transaction_id": "<string>",
    "reviewer_id": "<string>",
    "reviewee_id": "<string>",
    "product_id": "<string>",
    "rating": "<integer 1-5>",
    "comment": "<string>",
    "created_at": "<datetime>"
  }
}
```

**Error Responses:** 401 | 404 `NOT_FOUND`


---

## 15. Reports — `/api/v1/reports`
All endpoints require `Authorization: Bearer <token>`.

#### `POST /api/v1/reports/`
Submits a report against a product or user for trust & safety moderation.

**Auth:** Required

**Request Body:**
```json
{
  "target_type": "PRODUCT | USER",
  "target_id": "<string>",
  "reason": "<string, max 100 chars>",
  "description": "<optional string, max 1000 chars>"
}
```

**Success (201):** `{ "success": true, "data": { "report_id": "<string>", "message": "Report submitted successfully." } }`

**Error Responses:** 401 | 400 `INVALID_TARGET_TYPE` / `INVALID_REASON` | 404 `NOT_FOUND` | 409 `DUPLICATE_REPORT`

---

#### `GET /api/v1/reports/<report_id>`
Retrieves detail of a single report. Accessible by the reporter or an admin.

**Auth:** Required (Reporter or Admin)

**Success (200):** `{ "success": true, "data": { ...report fields... } }`

**Error Responses:** 401 | 403 `FORBIDDEN` | 404 `NOT_FOUND`

---

## 16. Admin & Analytics — `/api/v1/admin`
All endpoints require `Authorization: Bearer <token>` AND user role `admin`.

Non-admin requests return `403 FORBIDDEN`.

---

#### `GET /api/v1/admin/users`
Paginated list of all users. Sanitized (never returns `password_hash`).

**Query Params:** `page` (default 1), `limit` (default 20), `role` (`student`/`admin`), `status` (`ACTIVE`/`SUSPENDED`)

**Success (200):** `{ "success": true, "data": { "items": [ { ...user fields... } ], "pagination": { ... } } }`

---

#### `GET /api/v1/admin/users/<user_id>`
Retrieve single user detail. Sanitized (no `password_hash`).

**Success (200):** `{ "success": true, "data": { ...user fields... } }`

---

#### `PATCH /api/v1/admin/users/<user_id>/status`
Updates account status of a user (`ACTIVE` or `SUSPENDED`).

**Request Body:** `{ "status": "ACTIVE | SUSPENDED" }`

**Business Rules:** Admin cannot suspend their own admin account.

---

#### `PATCH /api/v1/admin/users/<user_id>/role`
Updates user role (`student` or `admin`).

**Request Body:** `{ "role": "student | admin" }`

**Business Rules:** Admin cannot demote their own admin account.

---

#### `GET /api/v1/admin/products`
Lists products for moderation, including `REMOVED` products.

**Query Params:** `page`, `limit`, `status`

---

#### `PATCH /api/v1/admin/products/<product_id>/status`
Moderates product status (`ACTIVE`, `RESERVED`, `SOLD`, `REMOVED`).

**Business Rules:** Cannot transition `SOLD` back to `ACTIVE` or `RESERVED`.

---

#### `GET /api/v1/admin/reports`
Lists moderation reports with optional filters for `status` and `target_type`.

---

#### `GET /api/v1/admin/reports/<report_id>`
Retrieve report detail.

---

#### `PATCH /api/v1/admin/reports/<report_id>/status`
Updates report status (`REVIEWING`, `RESOLVED`, `DISMISSED`). Records `resolved_by` and `resolved_at`.

---

#### `GET /api/v1/admin/categories`
Lists all categories including inactive ones.

---

#### `POST /api/v1/admin/categories`
Creates a new category.

**Request Body:** `{ "name": "<string>", "slug": "<string>", "description": "<string>", "icon": "<string>" }`

---

#### `PATCH /api/v1/admin/categories/<slug>`
Updates category fields or `is_active` status.

---

#### `GET /api/v1/admin/analytics/overview`
Aggregated marketplace overview metrics computed dynamically via MongoDB queries.

**Success (200):**
```json
{
  "success": true,
  "data": {
    "users": { "total": 10, "active": 9, "suspended": 1, "students": 8, "admins": 2 },
    "products": { "total": 15, "active": 10, "reserved": 2, "sold": 2, "removed": 1 },
    "transactions": { "total": 5, "pending": 1, "reserved": 2, "completed": 2, "cancelled": 0 },
    "purchase_requests": { "total": 8, "pending": 2, "accepted": 4, "rejected": 1, "cancelled": 1 },
    "reviews": { "total": 4, "average_rating": 4.5 },
    "reports": { "total": 2, "open": 1 },
    "categories": [ { "category_id": "textbooks", "name": "Textbooks", "product_count": 8 } ]
  }
}
```

---

## 17. Future Endpoint Organization (Planned Phase 9+)
- `/api/v1/analytics/insights` - AI/ML price predictions and recommendations (Phase 9)

