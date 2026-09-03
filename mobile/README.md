# SecondSpin Mobile Application (Phase 11)

Production-ready Flutter mobile application for **SecondSpin** — a campus-exclusive marketplace where college students buy, sell, and exchange pre-owned student essentials.

## System Architecture

```
React Web Application ──────┐
                            ▼
                     Flask REST API (/api/v1)
                            │
                            ▼
                     MongoDB Atlas
                            ▲
                            │
Flutter Mobile App ─────────┘
```

The Flutter mobile application connects directly to the existing Flask REST API (`/api/v1`) using standard HTTP endpoints and JSON response envelopes. It shares the exact same backend, MongoDB database, models, and business logic as the React web application.

## Folder Structure

```
mobile/
├── android/
├── ios/
├── lib/
│   ├── core/
│   │   ├── config/          # AppConfig (Base URL, Emulator IP settings)
│   │   ├── constants/       # AppColors (Material 3 emerald brand palette)
│   │   ├── network/         # ApiClient (HTTP fetch wrapper with JWT Bearer injection)
│   │   └── utils/
│   ├── models/              # UserModel, ProductModel, CategoryModel, Wishlist, Request, Transaction, Review, Report, Smart
│   ├── services/            # Domain network services (auth, products, wishlist, requests, transactions, reviews, smart, admin)
│   ├── providers/           # AuthProvider, MarketplaceProvider, WishlistProvider
│   ├── widgets/             # StatusBadge, ProductCard, RatingStars
│   ├── features/
│   │   ├── auth/            # LoginScreen, RegisterScreen
│   │   ├── home/            # HomeScreen (Hero, Search, Popular Products, Smart Recommendations)
│   │   ├── marketplace/     # MarketplaceScreen, SellScreen
│   │   ├── product/         # ProductDetailScreen (Gallery, Price Insights, Request to Buy, Related Items, Report)
│   │   ├── wishlist/        # WishlistScreen
│   │   ├── requests/        # RequestsScreen (Buyer & Seller tabs)
│   │   ├── transactions/    # TransactionsScreen (Purchases & Sales, Reserve, Complete, Review Modal)
│   │   ├── profile/         # ProfileScreen
│   │   └── admin/           # AdminDashboardScreen (Analytics Overview, Users, Moderation)
│   └── main.dart            # Entrypoint & Bottom Navigation Scaffold
├── test/
│   └── unit_test.dart       # Model deserialization, status mappings, and fallback tests
├── .env.example
├── pubspec.yaml
└── README.md
```

## Setup & Local Development

1. **Install Flutter SDK**: Ensure Flutter 3.x+ and Dart 3.x+ are installed and added to your system PATH.
2. **Fetch Dependencies**:
   ```bash
   cd mobile
   flutter pub get
   ```
3. **Configure API Endpoint**:
   - **Android Emulator**: Uses `http://10.0.2.2:5000/api/v1` by default in `AppConfig`.
   - **iOS Simulator**: Uses `http://127.0.0.1:5000/api/v1` by default in `AppConfig`.
   - **Physical Device**: Update `AppConfig.setCustomBaseUrl('http://<your-computer-ip>:5000/api/v1')`.

4. **Run Development App**:
   ```bash
   flutter run
   ```

5. **Run Test Suite**:
   ```bash
   flutter test
   ```

## Authentication & Security

- **JWT Session**: Auth tokens are stored locally via `SharedPreferences`.
- **Bearer Header**: Attached automatically to requests via `ApiClient`.
- **401 Handling**: Clears saved token and forces `AuthProvider` to reset state cleanly.
- **Role Enforcement**: Backend performs strict authorization checks.
