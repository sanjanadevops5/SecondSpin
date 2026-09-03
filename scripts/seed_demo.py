import os
import sys
import datetime
from werkzeug.security import generate_password_hash

# Add project root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models.user import UserModel
from backend.models.category import CategoryModel
from backend.models.product import ProductModel
from backend.models.wishlist import WishlistModel
from backend.models.purchase_request import PurchaseRequestModel
from backend.models.transaction import TransactionModel
from backend.models.review import ReviewModel
from backend.models.report import ReportModel

DEMO_PASSWORD = "Password123!"

INITIAL_CATEGORIES = [
    {"name": "Textbooks", "slug": "textbooks"},
    {"name": "Scientific Calculators", "slug": "scientific-calculators"},
    {"name": "Electronics", "slug": "electronics"},
    {"name": "Laptops", "slug": "laptops"},
    {"name": "Bicycles", "slug": "bicycles"},
    {"name": "Lab Equipment", "slug": "lab-equipment"},
    {"name": "Hostel Essentials", "slug": "hostel-essentials"},
    {"name": "Stationery", "slug": "stationery"},
    {"name": "Sports Equipment", "slug": "sports-equipment"},
    {"name": "Other", "slug": "other"},
]

DEMO_USERS = [
    {
        "name": "SecondSpin Admin",
        "email": "admin@demo.secondspin.local",
        "role": "admin",
        "department": "Campus Operations",
        "verification_status": "VERIFIED",
        "account_status": "ACTIVE",
    },
    {
        "name": "Aarav Mehta",
        "email": "seller1@demo.secondspin.local",
        "role": "student",
        "department": "Computer Science",
        "verification_status": "VERIFIED",
        "account_status": "ACTIVE",
    },
    {
        "name": "Riya Sharma",
        "email": "seller2@demo.secondspin.local",
        "role": "student",
        "department": "Electrical Engineering",
        "verification_status": "VERIFIED",
        "account_status": "ACTIVE",
    },
    {
        "name": "Kabir Singh",
        "email": "buyer1@demo.secondspin.local",
        "role": "student",
        "department": "Mechanical Engineering",
        "verification_status": "VERIFIED",
        "account_status": "ACTIVE",
    },
    {
        "name": "Ananya Patel",
        "email": "buyer2@demo.secondspin.local",
        "role": "student",
        "department": "Business Administration",
        "verification_status": "VERIFIED",
        "account_status": "ACTIVE",
    },
]


def seed_demo_data():
    app = create_app()
    with app.app_context():
        print("==================================================")
        print("  SECONDSPIN — SAFE DEMO DATA SEEDING SYSTEM      ")
        print("==================================================")

        now = datetime.datetime.now(datetime.timezone.utc)
        pass_hash = generate_password_hash(DEMO_PASSWORD)

        # 1. Seed Categories
        print("\n[1/7] Seeding Categories...")
        cat_coll = CategoryModel.collection()
        cat_coll.create_index("slug", unique=True)
        cat_map = {}
        for c in INITIAL_CATEGORIES:
            existing = cat_coll.find_one({"slug": c["slug"]})
            if not existing:
                doc = {
                    "name": c["name"],
                    "slug": c["slug"],
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                }
                res = cat_coll.insert_one(doc)
                cat_map[c["slug"]] = str(res.inserted_id)
            else:
                cat_map[c["slug"]] = str(existing["_id"])
        print(f"[OK] Categories ready ({len(cat_map)} categories).")

        # 2. Seed Demo Users
        print("\n[2/7] Seeding Demo Users...")
        user_coll = UserModel.collection()
        user_coll.create_index("email", unique=True)
        user_map = {}

        for u in DEMO_USERS:
            existing = user_coll.find_one({"email": u["email"]})
            if not existing:
                doc = {
                    "name": u["name"],
                    "email": u["email"],
                    "password_hash": pass_hash,
                    "role": u["role"],
                    "department": u["department"],
                    "verification_status": u["verification_status"],
                    "account_status": u["account_status"],
                    "created_at": now,
                    "updated_at": now,
                }
                res = user_coll.insert_one(doc)
                user_map[u["email"]] = str(res.inserted_id)
                print(f"  + Created User: {u['name']} ({u['email']})")
            else:
                user_map[u["email"]] = str(existing["_id"])
                print(f"  ~ Existing User: {u['name']} ({u['email']})")

        seller1_id = user_map["seller1@demo.secondspin.local"]
        seller2_id = user_map["seller2@demo.secondspin.local"]
        buyer1_id = user_map["buyer1@demo.secondspin.local"]
        buyer2_id = user_map["buyer2@demo.secondspin.local"]

        # 3. Seed Marketplace Products
        print("\n[3/7] Seeding Marketplace Products...")
        prod_coll = ProductModel.collection()

        demo_products = [
            {
                "title": "Engineering Mathematics (8th Edition)",
                "description": "Essential textbook for CS/EE/ME math modules. Excellent condition, no highlighting.",
                "price": 35.00,
                "category_id": cat_map["textbooks"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "TI-84 Plus CE Graphing Calculator",
                "description": "Full color display graphing calculator. Comes with USB charging cable.",
                "price": 55.00,
                "category_id": cat_map["scientific-calculators"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1594980596870-8aa52a78d8cd?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Data Structures & Algorithms in Java",
                "description": "Classic textbook by Goodrich & Tamassia. Perfect for CS201 course.",
                "price": 40.00,
                "category_id": cat_map["textbooks"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Arduino Uno Complete Starter Kit",
                "description": "Includes breadboard, jumper wires, sensors, LEDs, and tutorial manual.",
                "price": 25.00,
                "category_id": cat_map["electronics"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1553406830-ef2513450d76?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Logitech MX Master 3 Wireless Mouse",
                "description": "Ergonomic Bluetooth mouse with hyper-fast scroll wheel. Battery lasts 2 months.",
                "price": 45.00,
                "category_id": cat_map["electronics"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Dell UltraSharp 24-inch FHD Monitor",
                "description": "IPS panel with HDMI & DisplayPort inputs. Ideal for dual screen laptop setup.",
                "price": 85.00,
                "category_id": cat_map["laptops"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Trek Campus Hybrid Bicycle",
                "description": "21-speed lightweight aluminum frame bike with front basket and u-lock.",
                "price": 110.00,
                "category_id": cat_map["bicycles"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Chemistry Lab Coat & Safety Goggles Set",
                "description": "White 100% cotton lab coat (Size M) and anti-fog safety goggles.",
                "price": 18.00,
                "category_id": cat_map["lab-equipment"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Hostel Room Study Lamp with USB Port",
                "description": "Dimmable LED desk lamp with touch controls and phone charging port.",
                "price": 15.00,
                "category_id": cat_map["hostel-essentials"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Wilson Pro Tennis Racket & Ball Set",
                "description": "Lightweight carbon fiber tennis racket with 3 fresh Wilson championship balls.",
                "price": 30.00,
                "category_id": cat_map["sports-equipment"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Casio FX-991EX ClassWiz Calculator",
                "description": "High resolution display scientific calculator with spreadsheet functions.",
                "price": 22.00,
                "category_id": cat_map["scientific-calculators"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1611125832047-1d7ad1e8e49d?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "North Face Campus Backpack 30L",
                "description": "Padded laptop sleeve, water resistant coating, ergonomic shoulder straps.",
                "price": 38.00,
                "category_id": cat_map["hostel-essentials"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Apple iPad Air (64GB WiFi, Space Gray)",
                "description": "Includes Apple Pencil 2nd gen. Screen protector installed since day 1.",
                "price": 320.00,
                "category_id": cat_map["laptops"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80"],
                "status": "RESERVED",
                "seller_id": seller1_id,
            },
            {
                "title": "Digital Multimeter & Circuit Tester Kit",
                "description": "Precision digital multimeter for EE hardware assignments.",
                "price": 20.00,
                "category_id": cat_map["electronics"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80"],
                "status": "SOLD",
                "seller_id": seller2_id,
            },
            {
                "title": "Inappropriate / Spam Test Listing",
                "description": "Demo product created for testing admin listing moderation & report resolution.",
                "price": 999.00,
                "category_id": cat_map["other"],
                "condition": "POOR",
                "images": ["https://images.unsplash.com/photo-1584824486509-112e4181ff6b?auto=format&fit=crop&w=600&q=80"],
                "status": "REMOVED",
                "seller_id": seller1_id,
            },
        ]

        prod_map = {}
        for p in demo_products:
            existing = prod_coll.find_one({"title": p["title"], "seller_id": p["seller_id"]})
            if not existing:
                doc = {
                    "title": p["title"],
                    "description": p["description"],
                    "price": p["price"],
                    "category_id": p["category_id"],
                    "condition": p["condition"],
                    "images": p["images"],
                    "status": p["status"],
                    "seller_id": p["seller_id"],
                    "created_at": now,
                    "updated_at": now,
                }
                res = prod_coll.insert_one(doc)
                prod_map[p["title"]] = str(res.inserted_id)
            else:
                prod_map[p["title"]] = str(existing["_id"])
        print(f"[OK] Seeded {len(demo_products)} demo products.")

        # 4. Seed Wishlists
        print("\n[4/7] Seeding Saved Wishlists...")
        wish_coll = WishlistModel.collection()
        calc_id = prod_map.get("TI-84 Plus CE Graphing Calculator")
        laptop_id = prod_map.get("Apple iPad Air (64GB WiFi, Space Gray)")
        bike_id = prod_map.get("Trek Campus Hybrid Bicycle")

        if calc_id and not wish_coll.find_one({"user_id": buyer1_id, "product_id": calc_id}):
            wish_coll.insert_one({"user_id": buyer1_id, "product_id": calc_id, "created_at": now})
        if laptop_id and not wish_coll.find_one({"user_id": buyer1_id, "product_id": laptop_id}):
            wish_coll.insert_one({"user_id": buyer1_id, "product_id": laptop_id, "created_at": now})
        if bike_id and not wish_coll.find_one({"user_id": buyer2_id, "product_id": bike_id}):
            wish_coll.insert_one({"user_id": buyer2_id, "product_id": bike_id, "created_at": now})

        print("[OK] Wishlist items seeded.")

        # 5. Seed Purchase Requests & Transactions
        print("\n[5/7] Seeding Purchase Requests & Transactions...")
        req_coll = PurchaseRequestModel.collection()
        tx_coll = TransactionModel.collection()

        # Completed Transaction for Multimeter
        mm_id = prod_map.get("Digital Multimeter & Circuit Tester Kit")
        if mm_id:
            req_doc = req_coll.find_one({"product_id": mm_id, "buyer_id": buyer1_id})
            if not req_doc:
                res = req_coll.insert_one({
                    "product_id": mm_id,
                    "buyer_id": buyer1_id,
                    "seller_id": seller2_id,
                    "message": "Hi! Can I pick this up from the EE lab building?",
                    "status": "ACCEPTED",
                    "created_at": now,
                    "updated_at": now,
                })
                pr_id = str(res.inserted_id)
            else:
                pr_id = str(req_doc["_id"])

            tx_doc = tx_coll.find_one({"purchase_request_id": pr_id})
            if not tx_doc:
                tx_res = tx_coll.insert_one({
                    "purchase_request_id": pr_id,
                    "product_id": mm_id,
                    "buyer_id": buyer1_id,
                    "seller_id": seller2_id,
                    "status": "COMPLETED",
                    "created_at": now,
                    "completed_at": now,
                    "updated_at": now,
                })
                tx_id = str(tx_res.inserted_id)
            else:
                tx_id = str(tx_doc["_id"])

            # 6. Seed Seller Review
            print("\n[6/7] Seeding Reviews...")
            rev_coll = ReviewModel.collection()
            if not rev_coll.find_one({"transaction_id": tx_id}):
                rev_coll.insert_one({
                    "transaction_id": tx_id,
                    "reviewer_id": buyer1_id,
                    "reviewee_id": seller2_id,
                    "product_id": mm_id,
                    "rating": 5,
                    "comment": "Super helpful student seller! Equipment was clean and worked perfectly.",
                    "created_at": now,
                })

        print("[OK] Purchase requests & transaction history seeded.")

        # 7. Seed Admin Reports
        print("\n[7/7] Seeding Admin Moderation Reports...")
        rep_coll = ReportModel.collection()
        spam_id = prod_map.get("Inappropriate / Spam Test Listing")
        if spam_id and not rep_coll.find_one({"target_id": spam_id}):
            rep_coll.insert_one({
                "reporter_id": buyer1_id,
                "target_type": "PRODUCT",
                "target_id": spam_id,
                "reason": "Spam or misleading listing price",
                "description": "Listing price is abnormal and description is placeholder text.",
                "status": "OPEN",
                "created_at": now,
                "updated_at": now,
            })

        print("[OK] Admin reports seeded.")

        print("\n==================================================")
        print("  DEMO SEED COMPLETE — ALL DATA READY FOR DEMO!   ")
        print("==================================================")


if __name__ == "__main__":
    seed_demo_data()
