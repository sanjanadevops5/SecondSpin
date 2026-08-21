# Feature Prioritization: SecondSpin

## Purpose
To provide an exhaustive list of features for the SecondSpin platform, categorized by domain and prioritized to guide the development phases.

## Context
Prioritization ensures the most critical paths (Auth, Listing, Requesting) are built first.
- **P0** = Must Have (MVP Core)
- **P1** = Important (Fast-follow, core experience enhancer)
- **P2** = Advanced (Polishes the product, adds "startup" feel)
- **P3** = Future (Out of scope for initial build)

## Current Status
Features prioritized.

---

### 1. Authentication & User Management
- **P0:** Student registration (Email, Password, Name).
- **P0:** Login/Logout with secure session/JWT.
- **P0:** Password hashing (bcrypt/argon2).
- **P0:** Basic profile management (update name, view own listings).
- **P1:** Role-based access (Student vs. Admin).
- **P1:** Student-focused verification (e.g., requiring `.edu` email).

### 2. Marketplace & Browsing
- **P0:** Create, edit, delete product listings.
- **P0:** Categorization (Textbooks, Electronics, Bicycles, etc.).
- **P0:** Product condition tags (New, Good, Fair).
- **P0:** Product images upload and viewing.
- **P0:** Basic Search (Title/Description).
- **P0:** Filtering by Category.
- **P0:** Product Status (Available, Reserved, Sold).
- **P1:** Sorting (Price High/Low, Newest).
- **P2:** Advanced Filtering (Price range, Condition).

### 3. Buyer Features
- **P0:** Send Purchase Request.
- **P1:** Wishlist (Save items for later).
- **P1:** Request tracking (Pending, Accepted, Rejected).
- **P1:** View Seller profile and active listings.
- **P2:** Transaction history (Items bought).
- **P2:** Leave Reviews and Ratings for sellers.

### 4. Seller Features
- **P0:** Accept/Reject purchase requests.
- **P0:** Mark products as Reserved/Sold.
- **P1:** Seller dashboard (consolidated view of listings and requests).
- **P2:** View transaction history (Items sold).

### 5. Trust & Safety
- **P1:** Report listing (inappropriate, spam).
- **P1:** Report user.
- **P2:** Seller ratings (aggregate score) display.
- **P2:** Written reviews display on seller profile.

### 6. Admin Features
- **P1:** Admin dashboard access.
- **P1:** Listing moderation (hide/delete listings).
- **P2:** User management (ban/suspend users).
- **P2:** View Reports queue.
- **P2:** Transaction analytics.
- **P2:** Category analytics and Marketplace statistics.

### 7. Smart Features
- **P2:** Similar/related product recommendations (based on metadata).
- **P2:** Popular products / Trending categories display.
- **P2:** Historical price insights (average price for a category).

### 8. Future Scope (P3)
- **P3:** AI product recommendations.
- **P3:** ML-based price prediction.
- **P3:** QR-based transaction verification.
- **P3:** Campus pickup points integration.
- **P3:** Push notifications.
- **P3:** In-app real-time chat.
- **P3:** Multi-campus marketplace support.
- **P3:** Advanced fraud detection.
