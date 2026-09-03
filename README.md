# SecondSpin — Campus-Exclusive Marketplace Platform

**SecondSpin** is a full-stack campus-exclusive marketplace platform built specifically for college students to buy, sell, and exchange pre-owned student essentials such as textbooks, scientific calculators, laptops, bicycles, hostel gear, lab equipment, and sports gear.

---

## Architecture Overview

```
                      ┌─── React 19 Responsive Web Application (Vite 8)
                      │
                      ▼
               Flask REST API (/api/v1)
                      │
                      ▼
               MongoDB Atlas
                      ▲
                      │
                      └─── Flutter Mobile Application (iOS & Android)
```

Both the **React Web Application** and **Flutter Mobile Application** communicate with the central **Flask REST API**, sharing authentication, data models, business rules, and MongoDB persistence.

---

## Core Product Capabilities

- **Authentication & Security**: Student email validation (`@univ.edu`), PBKDF2/Bcrypt password hashing, JWT Bearer tokens, and Role-Based Access Control (`STUDENT` / `ADMIN`).
- **Marketplace Engine**: Listing creation, image management, category taxonomy, condition grading (`NEW`, `LIKE_NEW`, `GOOD`, `FAIR`, `POOR`), price filtering, multi-field search, sorting, and status lifecycle (`ACTIVE`, `RESERVED`, `SOLD`, `REMOVED`).
- **Saved Wishlist**: Instant add/remove wishlist management with duplicate prevention.
- **Purchase Request Hub**: Buyer purchase request submission, seller accept/reject controls, buyer cancellation.
- **Transaction Lifecycle**: Seamless transition from accepted request to transaction (`PENDING` -> `RESERVED` -> `COMPLETED`).
- **Reviews & Ratings**: 1–5 star rating system and student seller reviews upon completed transactions.
- **Smart Marketplace Features**: Rule-driven Related Products, Trending Items, Historical Price Insights, and Personalized Recommendations with cold-start fallbacks.
- **Admin Control Center**: Real-time platform analytics metrics, user account moderation (suspend/unsuspend), listing moderation, and report resolution.

---

## Project Structure

```
SecondSpin/
├── backend/                  # Flask REST API source code & blueprints
├── web/                      # React 19 + TypeScript + Vite web app
├── mobile/                   # Flutter mobile app
├── database/                 # MongoDB schema specifications & indexes
├── docs/                     # PRD, Architecture, API Guide, Demo Guide
├── scripts/                  # Demo seeding & index setup scripts
├── tests/                    # Backend regression test suite (196 tests)
└── venv/                     # Python virtual environment
```

---

## Quick Start & Local Demo Instructions

### 1. Seed Demo Data
```powershell
venv\Scripts\python.exe scripts/seed_demo.py
```

### 2. Start Backend API
```powershell
venv\Scripts\python.exe -m backend.app
```
- **API Base URL**: `http://127.0.0.1:5000/api/v1`
- **Health Endpoint**: `http://127.0.0.1:5000/api/v1/health`

### 3. Start Web Application
```powershell
cd web
npm run dev
```
- **Web App URL**: `http://localhost:3000`

### 4. Local Demo Accounts (Password: `Password123!`)
- **Admin**: `admin@demo.secondspin.local`
- **Seller 1**: `seller1@demo.secondspin.local` (Aarav Mehta)
- **Seller 2**: `seller2@demo.secondspin.local` (Riya Sharma)
- **Buyer 1**: `buyer1@demo.secondspin.local` (Kabir Singh)
- **Buyer 2**: `buyer2@demo.secondspin.local` (Ananya Patel)
