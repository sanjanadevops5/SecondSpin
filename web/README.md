# SecondSpin Web Application (Phase 10)

Production-grade responsive React web application for **SecondSpin** — a campus-exclusive marketplace where college students buy, sell, and exchange pre-owned student essentials.

## Technology Stack

- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 8
- **Routing**: React Router DOM 7
- **Styling**: Tailwind CSS v4 (Vanilla utility classes with custom HSL brand tokens)
- **Icons**: Lucide React
- **API Client**: Centralized native `fetch` wrapper (`services/api.ts`) with automatic JWT Bearer authentication headers and 401 token handling.

## Folder Structure

```
web/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── common/         # Badge, ProductCard, RatingStars, Modal, Route Guards
│   │   └── layout/         # Navbar, Footer
│   ├── context/            # AuthContext (JWT session persistence)
│   ├── pages/
│   │   ├── Auth/           # Login, Register
│   │   ├── Admin/          # AdminDashboard (Users, Listings, Reports, Analytics)
│   │   ├── Home.tsx        # Hero, Search, Categories, Popular Products, Recommendations
│   │   ├── Marketplace.tsx # Search, Category/Condition/Price filters, Pagination
│   │   ├── ProductDetail.tsx# Image gallery, Price Insights, Related Products, Purchase Request & Report modals
│   │   ├── Sell.tsx        # Create & Edit listing form
│   │   ├── Wishlist.tsx    # Saved student wishlist
│   │   ├── Requests.tsx    # Buyer & Seller purchase requests
│   │   ├── Transactions.tsx# Buyer & Seller transaction history & review submission
│   │   └── Profile.tsx     # Student profile & active listings
│   ├── services/           # Domain API clients (auth, products, wishlist, requests, transactions, reviews, reports, smart, admin)
│   ├── types/              # TypeScript interfaces matching backend models
│   ├── App.tsx             # Main client routes
│   └── main.tsx            # Entrypoint
├── .env.example
├── package.json
├── tsconfig.json
└── vite.config.ts          # Vite configuration with API proxy settings
```

## Setup & Running Locally

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Environment**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```
   The dev server will run at `http://localhost:3000`. Requests to `/api/v1` are automatically proxied to the Flask backend running at `http://127.0.0.1:5000`.

4. **Production Build**:
   ```bash
   npm run build
   ```

## Authentication & API Integration

- **JWT Session**: Auth tokens are stored in `localStorage` under `secondspin_token`.
- **Automatic Headers**: The central API client (`services/api.ts`) automatically injects `Authorization: Bearer <token>` for all authenticated endpoints.
- **401 Unauthorized Handling**: If an auth token expires or becomes invalid, the API client automatically clears the token and dispatches an event to reset `AuthContext`.
