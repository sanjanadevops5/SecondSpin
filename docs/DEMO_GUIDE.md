# SecondSpin Local Demo & Presentation Guide

This guide provides step-by-step instructions to seed demo data, start the application, and present a complete live demonstration of **SecondSpin** (campus-exclusive marketplace).

---

## 1. Seed Safe Demo Data

Run the safe, repeatable demo data seeding command:

```powershell
cd c:\Users\Sanju\Desktop\SecondSpin
venv\Scripts\python.exe scripts/seed_demo.py
```

This populates:
- **10 Categories**: Textbooks, Scientific Calculators, Electronics, Laptops & Computers, Bicycles, Lab Equipment, Hostel Essentials, Stationery, Sports Equipment, Accessories & Other.
- **5 Verified Demo Accounts**: 1 Admin, 2 Student Sellers, 2 Student Buyers.
- **26 Realistic Student Marketplace Listings**: 19 ACTIVE, 3 RESERVED, 2 SOLD, 1 REMOVED.
- **Wishlists, Purchase Requests, Transactions, Reviews, and Moderation Reports**.

---

## 2. Pre-Configured Demo Credentials

**Standard Password for All Demo Accounts**: `Password123!`

| Role | Name | Email | Department |
|---|---|---|---|
| **Admin** | SecondSpin Admin | `admin@demo.secondspin.local` | Campus Operations |
| **Seller 1** | Aarav Mehta | `seller1@demo.secondspin.local` | Computer Science |
| **Seller 2** | Riya Sharma | `seller2@demo.secondspin.local` | Electrical Engineering |
| **Buyer 1** | Kabir Singh | `buyer1@demo.secondspin.local` | Mechanical Engineering |
| **Buyer 2** | Ananya Patel | `buyer2@demo.secondspin.local` | Business Administration |

---

## 3. Launch Application Stack

### Terminal 1 — Backend API
```powershell
cd c:\Users\Sanju\Desktop\SecondSpin
venv\Scripts\python.exe -m backend.app
```
- **Base URL**: `http://127.0.0.1:5000/api/v1`
- **Health Check**: `http://127.0.0.1:5000/api/v1/health`
- **Categories Endpoint**: `http://127.0.0.1:5000/api/v1/categories/`

### Terminal 2 — Web Application
```powershell
cd c:\Users\Sanju\Desktop\SecondSpin\web
npm run dev
```
- **Web App URL**: `http://localhost:3000`

---

## 4. Live Presentation Sequence

1. **Open Application**: Navigate to `http://localhost:3000`.
2. **Explore Marketplace**: Browse pre-seeded listings, search for *"calculator"*, filter by category (*Textbooks*, *Electronics*, *Bicycles*), and sort by price (*Low to High*).
3. **Inspect Product Detail**: Click on *"TI-84 Plus CE Graphing Calculator"* or *"Lenovo ThinkPad E14 Laptop"* to demonstrate historical price insights and related campus products.
4. **Log In as Seller**: Click **Login** and sign in as `seller1@demo.secondspin.local` / `Password123!`.
5. **Demonstrate "Sell Item"**: Click **Sell Item**. Show the **Category dropdown** loading real backend categories (*Textbooks*, *Scientific Calculators*, *Electronics*, *Laptops & Computers*, etc.). Fill in title, category, condition, price, description, image URL, and submit.
6. **Verify New Listing**: Return to **Marketplace** to show the newly published listing.
7. **Switch to Buyer & Request to Buy**: Log in as `buyer1@demo.secondspin.local` / `Password123!`, save items to wishlist, and click **Request to Buy**.
8. **Seller Request Acceptance & Transaction**: Switch to `seller1@demo.secondspin.local`, view incoming requests, click **Accept**, reserve the item, and complete the sale.
9. **Post Seller Review**: Switch back to `buyer1@demo.secondspin.local`, go to **Orders**, and leave a 5-star rating.
10. **Admin Moderation & Analytics**: Log in as `admin@demo.secondspin.local`, open `/admin` to demonstrate live metrics overview, user status moderation, and report resolution.
