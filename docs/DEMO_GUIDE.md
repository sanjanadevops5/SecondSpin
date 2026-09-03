# SecondSpin Local Demo Guide

This guide provides step-by-step instructions to run and demo the full **SecondSpin** campus marketplace stack locally.

---

## Prerequisites

1. **Python 3.10+**: Virtual environment located at `venv/`.
2. **Node.js 18+ & npm**: For running the React web application in `web/`.
3. **Flutter 3.x+ (Optional for Mobile)**: For running the Flutter mobile application in `mobile/`.

---

## 1. Start Flask REST API Backend

Open **Terminal 1** and run:

```powershell
cd c:\Users\Sanju\Desktop\SecondSpin
venv\Scripts\python.exe -m backend.app
```

- **Backend Base URL**: `http://127.0.0.1:5000/api/v1`
- **Health Check URL**: `http://127.0.0.1:5000/api/v1/health`

*(Note: The backend automatically falls back to an in-memory MongoDB mock if `MONGODB_URI` environment variable is omitted or unavailable, allowing out-of-the-box local demoing).*

---

## 2. Start React Web Application

Open **Terminal 2** and run:

```powershell
cd c:\Users\Sanju\Desktop\SecondSpin\web
npm run dev
```

- **Web App URL**: `http://localhost:3000`
- **Proxy**: `/api/v1` requests are automatically proxied by Vite to `http://127.0.0.1:5000`.

---

## 3. Start Flutter Mobile Application (Optional)

Open **Terminal 3** and run:

```powershell
cd c:\Users\Sanju\Desktop\SecondSpin\mobile
flutter run
```

- **Android Emulator Networking**: The Flutter app automatically targets `http://10.0.2.2:5000/api/v1` when running on an Android emulator.
- **iOS Simulator / Desktop**: Targets `http://127.0.0.1:5000/api/v1`.

---

## 4. Complete Demo Workflow

1. **Open Browser**: Navigate to `http://localhost:3000`.
2. **Student Registration**: Click **Register** and create a student account (e.g. `alex@univ.edu`, password `password123`).
3. **Browse Marketplace**: Search for items, apply category filters (`Textbooks`, `Electronics`, `Calculators`), and condition filters (`Good`, `Like New`).
4. **View Product Details**: Click any product card to inspect historical price insights, seller department info, and related campus items.
5. **Post a New Listing**: Click **Sell Item** and post a listing with title, category, price, condition, and image URL.
6. **Submit Purchase Request**: Log into a second student account, open a listing, and submit a "Request to Buy".
7. **Complete Transaction**: Log back in as seller, open **Requests**, click **Accept**, initiate transaction, click **Reserve Item**, and click **Complete Sale**.
8. **Leave Review**: Log back in as buyer, open **Orders**, and submit a 5-star seller review.
9. **Admin Dashboard**: Log in with an admin account and open `/admin` to view platform analytics metrics, user moderation (suspend/unsuspend), and listing moderation.
