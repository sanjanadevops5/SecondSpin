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

## 13. Future Endpoint Organization (Planned)
- `/api/v1/transactions` - Completed sales
- `/api/v1/reviews` - Ratings and feedback
- `/api/v1/reports` - Content moderation
- `/api/v1/admin` - Administrative actions
- `/api/v1/analytics` - Platform metrics

