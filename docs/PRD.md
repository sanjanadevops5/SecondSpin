# Product Requirements Document (PRD): SecondSpin

## Purpose
To define the comprehensive product requirements for SecondSpin, ensuring alignment on vision, scope, user needs, and technical deliverables before engineering begins.

## Current Status
**Draft / V1.0**

---

### 1. Executive Summary
SecondSpin is a campus-exclusive marketplace application (Web & Mobile) that enables college students to buy, sell, and exchange pre-owned items safely within their college community. By requiring student verification, SecondSpin fosters a high-trust environment tailored to the unique lifecycle of academic and hostel necessities.

### 2. Product Vision
To be the default, trusted ecosystem for every college student to sustainably cycle their academic and living essentials, reducing waste and financial burden.

### 3. Problem Statement
College students constantly cycle through expensive, temporary necessities (textbooks, calculators, lab gear, dorm items). Existing solutions suffer from a lack of trust, risk of scams, and inconvenient logistics for item handoffs.

### 4. Target Users
- **College Students (Undergraduate & Postgraduate):** The primary buyers and sellers.
- **Platform Administrators:** Managing users, moderating content, and overseeing platform safety.

### 5. User Personas
- **"Freshman Fiona" (Buyer):** Needs to buy textbooks, a bicycle, and a mini-fridge cheaply. Values trust and proximity.
- **"Senior Sam" (Seller):** Graduating and needs to liquidate his dorm items and 4 years of textbooks quickly. Values ease of listing and guaranteed campus buyers.

### 6. User Pain Points
- High cost of brand-new textbooks and equipment.
- Fear of being scammed on public internet marketplaces.
- Difficulty coordinating meeting spots with strangers.
- Hassle of packing and shipping items.

### 7. Proposed Solution
A hyper-local, campus-gated marketplace where every user is a verified student. Buyers and sellers can easily coordinate on-campus meetups to exchange goods, supported by a system of verified profiles, ratings, and targeted categories.

### 8. Value Proposition
- **Trust & Safety:** Exclusive to verified campus members.
- **Convenience:** Zero shipping; all transactions are campus-local.
- **Relevance:** Categories explicitly tailored to student life (e.g., Lab Equipment, Course Materials).

### 9. Goals
- Launch a stable Web and Flutter app sharing a single backend.
- Provide a frictionless listing experience (under 2 minutes to list an item).
- Establish a trustworthy rating and review system.

### 10. Non-Goals
- Handling payment processing (transactions are peer-to-peer/offline in MVP).
- Shipping or delivery logistics.
- Serving non-student or off-campus populations.

### 11. Functional Requirements
- User authentication and role management (Student, Admin).
- Create, read, update, delete (CRUD) operations for product listings.
- Search, filter, and sort capabilities for listings.
- Purchase requests and status tracking (Available, Reserved, Sold).
- User rating and review system.
- Moderation tools (reporting listings/users).

### 12. Non-Functional Requirements
- **Performance:** API response time < 300ms for core marketplace queries.
- **Scalability:** Capable of handling peak loads at the start/end of semesters.
- **Security:** Passwords securely hashed; secure session/token management.
- **Usability:** Responsive web design; native-feeling mobile app.

### 13. User Stories
- As a student, I want to filter items by category so I can easily find textbooks.
- As a seller, I want to mark an item as "Reserved" so others know a sale is pending.
- As a buyer, I want to see the seller's rating to trust the transaction.
- As an admin, I want to view reported listings so I can remove inappropriate content.

### 14. User Journeys
**Buying an Item:**
1. User logs in.
2. Browses/Searches for "Scientific Calculator".
3. Reviews item details and seller rating.
4. Sends a "Purchase Request".
5. Meets seller on campus to exchange.
6. Seller marks item "Sold".
7. Buyer leaves a review for the seller.

### 15. Feature Prioritization
*(Refer to `FEATURES.md` for the full breakdown)*
- **P0:** Auth, Listing CRUD, Search/Filter, Purchase Requests.
- **P1:** Wishlist, Ratings, Admin Moderation.
- **P2:** Analytics, Historical Price Insights.
- **P3 (Future):** In-app chat, ML recommendations.

### 16. MVP Definition
A functional marketplace where verified students can post items with images, browse/search listings, request to buy items, and manage basic profiles without integrated payments.

### 17. Advanced Features
Smart recommendations, price insights, detailed marketplace analytics, and comprehensive trust/safety reporting mechanisms.

### 18. Future Scope
In-app messaging, AI-based price predictions, QR verification for handoffs, and multi-campus scaling.

### 19. Success Metrics
- Number of active listings.
- Time-to-sell (average duration from listed to sold).
- Monthly Active Users (MAU).
- User report rate (trust/safety metric).

### 20. Risks
- **Cold Start Problem:** Having buyers but no sellers, or vice versa.
- **Trust Incidents:** Scams occurring despite verification, damaging reputation.

### 21. Assumptions
- Students have campus email addresses or IDs for verification.
- Students are willing to meet in person on campus for exchanges.
- A single backend can efficiently serve both Web and Flutter frontends.

### 22. Dependencies
- MongoDB Atlas availability.
- Cloud hosting for Flask API.
- Flutter SDK and cross-platform compilation tools.

### 23. Acceptance Criteria
- Web and mobile apps can successfully authenticate the same user.
- A listing created on mobile appears instantly on the web application.
- State changes (e.g., Available -> Sold) accurately reflect across all platforms.
