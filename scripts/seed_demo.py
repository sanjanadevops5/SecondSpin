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
    {"name": "Laptops & Computers", "slug": "laptops"},
    {"name": "Bicycles", "slug": "bicycles"},
    {"name": "Lab Equipment", "slug": "lab-equipment"},
    {"name": "Hostel Essentials", "slug": "hostel-essentials"},
    {"name": "Stationery", "slug": "stationery"},
    {"name": "Sports Equipment", "slug": "sports-equipment"},
    {"name": "Accessories & Other", "slug": "other"},
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
        print("  SECONDSPIN -- SAFE DEMO DATA SEEDING SYSTEM     ")
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
            # TEXTBOOKS (6 items)
            {
                "title": "Engineering Mathematics (8th Edition)",
                "description": "Essential textbook for CS/EE/ME math modules. Excellent condition with zero markings.",
                "price": 32.00,
                "category_id": cat_map["textbooks"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Data Structures and Algorithms in Java",
                "description": "Standard CS textbook by Goodrich & Tamassia. Covers trees, graphs, and dynamic programming.",
                "price": 28.00,
                "category_id": cat_map["textbooks"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Operating System Concepts (Silberschatz)",
                "description": "The dinosaur operating systems book! Great condition, required for CS302.",
                "price": 35.00,
                "category_id": cat_map["textbooks"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Database Management Systems (Ramakrishnan)",
                "description": "Comprehensive DBMS textbook covering SQL, relational algebra, and indexing.",
                "price": 24.00,
                "category_id": cat_map["textbooks"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Computer Networks (Tanenbaum 5th Ed)",
                "description": "Covers TCP/IP, routing algorithms, wireless networks, and network security.",
                "price": 30.00,
                "category_id": cat_map["textbooks"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Programming in Python (2nd Edition)",
                "description": "Introduction to Python programming, data structures, and computer science concepts.",
                "price": 20.00,
                "category_id": cat_map["textbooks"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1526379095098-d400fd0bf935?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },

            # SCIENTIFIC CALCULATORS (2 items)
            {
                "title": "TI-84 Plus CE Graphing Calculator",
                "description": "High-resolution color backlit display. Perfect for calculus and statistics. Includes USB cable.",
                "price": 48.00,
                "category_id": cat_map["scientific-calculators"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1594980596870-8aa52a78d8cd?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Casio FX-991EX ClassWiz Calculator",
                "description": "552 functions, high resolution LCD display, QR code equation display.",
                "price": 18.00,
                "category_id": cat_map["scientific-calculators"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1611125832047-1d7ad1e8e49d?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },

            # ELECTRONICS & HARDWARE (5 items)
            {
                "title": "Arduino Ultimate Hardware Starter Kit",
                "description": "Complete electronic components box: Uno board, breadboard, resistors, LEDs, motors, and sensors.",
                "price": 26.00,
                "category_id": cat_map["electronics"],
                "condition": "NEW",
                "images": ["https://images.unsplash.com/photo-1553406830-ef2513450d76?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Electronics Lab Breadboard & Component Set",
                "description": "Includes jumper wires, capacitors, transistors, IC chips, and logic gate ICs.",
                "price": 22.00,
                "category_id": cat_map["electronics"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Anker 7-in-1 USB-C Hub Adapter",
                "description": "HDMI 4K, 100W Power Delivery, SD Card reader, 2x USB 3.0 ports.",
                "price": 20.00,
                "category_id": cat_map["electronics"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1616440342230-016f1082531d?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Logitech K380 Multi-Device Wireless Keyboard",
                "description": "Compact Bluetooth keyboard for tablet or laptop setup.",
                "price": 22.00,
                "category_id": cat_map["electronics"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "SanDisk 1TB External USB 3.0 Portable SSD",
                "description": "High-speed portable SSD drive for data backups and OS ISO images.",
                "price": 65.00,
                "category_id": cat_map["electronics"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },

            # LAPTOPS & COMPUTERS (3 items)
            {
                "title": "Lenovo ThinkPad E14 Laptop (16GB RAM, 512GB SSD)",
                "description": "Fast i5 processor, crisp 1080p display, long battery life. Excellent for coding and assignments.",
                "price": 380.00,
                "category_id": cat_map["laptops"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Dell 24-inch UltraSharp Full HD Monitor",
                "description": "IPS panel with ultra-thin bezel, height adjustable stand, HDMI & DisplayPort.",
                "price": 95.00,
                "category_id": cat_map["laptops"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "Apple iPad Air (64GB WiFi, Space Gray)",
                "description": "Includes Apple Pencil 2nd gen and smart folio magnetic case. Currently reserved for campus buyer.",
                "price": 310.00,
                "category_id": cat_map["laptops"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80"],
                "status": "RESERVED",
                "seller_id": seller1_id,
            },

            # BICYCLES (1 item)
            {
                "title": "Trek Campus Hybrid Commuter Bicycle",
                "description": "Lightweight alloy frame, 21 speeds, front basket, and heavy-duty U-lock included.",
                "price": 120.00,
                "category_id": cat_map["bicycles"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },

            # LAB EQUIPMENT (2 items)
            {
                "title": "Chemistry Lab Coat & Anti-Fog Goggles Set",
                "description": "Unisex 100% white cotton lab coat (Size Medium) with clear safety goggles.",
                "price": 16.00,
                "category_id": cat_map["lab-equipment"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Physics Laboratory Equipment & Optical Prism Kit",
                "description": "Complete optics kit with glass prisms, lenses, and laser pointer.",
                "price": 25.00,
                "category_id": cat_map["lab-equipment"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1507668077129-56e32842fceb?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },

            # HOSTEL ESSENTIALS & STATIONERY (3 items)
            {
                "title": "Adjustable LED Hostel Study Desk Lamp",
                "description": "Touch switch LED lamp with 3 brightness modes and built-in USB charging port.",
                "price": 14.00,
                "category_id": cat_map["hostel-essentials"],
                "condition": "LIKE_NEW",
                "images": ["https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },
            {
                "title": "North Face Campus Backpack 30L",
                "description": "Padded laptop sleeve, water resistant coating, ergonomic shoulder straps.",
                "price": 38.00,
                "category_id": cat_map["hostel-essentials"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80"],
                "status": "RESERVED",
                "seller_id": seller1_id,
            },
            {
                "title": "Hostel Room Desk Fan (Quiet 3-Speed)",
                "description": "Compact desk fan for warm study sessions.",
                "price": 12.00,
                "category_id": cat_map["hostel-essentials"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1618941723380-496e5797f743?auto=format&fit=crop&w=600&q=80"],
                "status": "RESERVED",
                "seller_id": seller2_id,
            },

            # SPORTS EQUIPMENT (2 items)
            {
                "title": "Wilson Pro Tennis Racket with Ball Canister",
                "description": "Standard adult size composite tennis racket. Includes 3 unopened Wilson Extra Duty balls.",
                "price": 32.00,
                "category_id": cat_map["sports-equipment"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller1_id,
            },
            {
                "title": "Adidas Size 5 Campus Football",
                "description": "Durable stitched football, holds air pressure perfectly.",
                "price": 15.00,
                "category_id": cat_map["sports-equipment"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1614632537197-38a17061c2bd?auto=format&fit=crop&w=600&q=80"],
                "status": "ACTIVE",
                "seller_id": seller2_id,
            },

            # SOLD Products (1 item)
            {
                "title": "Digital Multimeter & Electrical Measurement Tool",
                "description": "Auto-ranging digital multimeter. Sold to engineering student.",
                "price": 19.00,
                "category_id": cat_map["electronics"],
                "condition": "GOOD",
                "images": ["https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80"],
                "status": "SOLD",
                "seller_id": seller2_id,
            },

            # REMOVED Products (1 item for moderation demo)
            {
                "title": "Inappropriate Spam Listing Demo Item",
                "description": "Spam listing created to test admin listing moderation and report resolution.",
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
        laptop_id = prod_map.get("Lenovo ThinkPad E14 Laptop (16GB RAM, 512GB SSD)")
        bike_id = prod_map.get("Trek Campus Hybrid Commuter Bicycle")

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

        mm_id = prod_map.get("Digital Multimeter & Electrical Measurement Tool")
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
        spam_id = prod_map.get("Inappropriate Spam Listing Demo Item")
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
        print("  DEMO SEED COMPLETE -- ALL DATA READY FOR DEMO!   ")
        print("==================================================")


if __name__ == "__main__":
    seed_demo_data()
