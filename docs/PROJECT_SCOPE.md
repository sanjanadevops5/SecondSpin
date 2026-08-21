# Project Scope: SecondSpin

## Purpose
To define the boundaries of the SecondSpin project, clearly delineating what is included in the MVP, what constitutes advanced functionality, and what is reserved for the future. This ensures the project remains realistically implementable by a single developer while maintaining a high standard of quality.

## Context
Scope creep is a major risk in marketplace applications. By strictly categorizing features, we ensure that the core value proposition is delivered robustly before complex, "nice-to-have" features are introduced.

## Current Status
Scope defined. Awaiting Phase 1 execution.

---

## 1. Minimum Viable Product (MVP) Scope

The MVP focuses on the absolute essentials required to facilitate a campus transaction.

**Included in MVP:**
- **Shared Architecture:** Flask REST API and MongoDB Atlas database.
- **Dual Frontends:** Basic Responsive Web App and Flutter Mobile App.
- **Authentication:** Standard email/password registration with JWT-based login and password hashing.
- **Marketplace Core:** 
  - Create, edit, delete product listings.
  - Image upload (single/multiple).
  - Basic categories (Textbooks, Electronics, etc.) and condition tags.
  - Search by keywords and filter by category.
- **Transaction Flow:** 
  - Buyers can send a "Purchase Request".
  - Sellers can Accept/Reject requests.
  - Sellers can manually update status: Available -> Reserved -> Sold.
- **Profiles:** Basic user profiles showing active listings.

## 2. Advanced Features Scope

Once the MVP is stable, these features will be implemented to elevate the platform from a basic CRUD app to a professional product.

**Included in Advanced Scope:**
- **Trust & Safety:** Seller ratings (1-5 stars) and text reviews post-transaction. User and listing reporting system.
- **Buyer Features:** Wishlist (save for later), transaction history.
- **Seller Features:** Seller dashboard with request management.
- **Admin Module:** Dedicated admin dashboard for user management, listing moderation, and basic marketplace statistics.
- **Smart Features:**
  - Historical price insights (e.g., "Calculators usually sell for $20").
  - "Similar products" recommendations based on category tags.
  - Trending/Popular categories display.

## 3. Future Scope (Out of Scope for Current Project)

These features represent the long-term vision but are explicitly excluded from the current development lifecycle to ensure project feasibility.

**Excluded from Current Project:**
- AI/ML product recommendations and price prediction.
- QR-code based transaction verification.
- Campus pickup point integrations.
- Real-time in-app chat (WebSockets).
- Push notifications.
- Integrated payment gateways (Stripe, PayPal).
- Multi-campus architecture and tenanting.
- Advanced fraud detection algorithms.

## Future Considerations
If development outpaces the schedule, select P2 (Advanced) features may be promoted to MVP. However, Future Scope items will strictly remain untouched unless specifically requested in a later phase.
