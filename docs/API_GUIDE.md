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
- `/api/v1/health` - Health check
- `/api/v1/auth/register` - User registration
- `/api/v1/auth/login` - User login
- `/api/v1/users/me` - User profile management
- `/api/v1/categories` - Product categories retrieval
- `/api/v1/products` - Marketplace discovery (search, filter, paginate) and creation
- `/api/v1/products/me` - Fetch authenticated user's listings
- `/api/v1/products/<id>` - Retrieve, update, and remove listings

## 13. Future Endpoint Organization (Planned)
- `/api/v1/wishlist` - User saved items
- `/api/v1/purchase-requests` - Offers on products
- `/api/v1/transactions` - Completed sales
- `/api/v1/reviews` - Ratings and feedback
- `/api/v1/reports` - Content moderation
- `/api/v1/admin` - Administrative actions
- `/api/v1/analytics` - Platform metrics
