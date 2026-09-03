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

# Canonical category definitions — slug is the primary key used as category_id in products
INITIAL_CATEGORIES = [
    {"name": "Textbooks", "slug": "textbooks"},
    {"name": "Scientific Calculators", "slug": "scientific-calculators"},
    {"name": "Electronics", "slug": "electronics"},
    {"name": "Laptops & Computers", "slug": "laptops-computers"},
    {"name": "Bicycles", "slug": "bicycles"},
    {"name": "Lab Equipment", "slug": "lab-equipment"},
    {"name": "Hostel Essentials", "slug": "hostel-essentials"},
    {"name": "Stationery", "slug": "stationery"},
    {"name": "Sports Equipment", "slug": "sports-equipment"},
    {"name": "Accessories & Other", "slug": "accessories"},
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
        print("  SECONDSPIN — SAFE DEMO DATA SEEDING SYSTEM       ")
        print("  Currency: INR (Rs)                                ")
        print("==================================================")

        now = datetime.datetime.now(datetime.timezone.utc)
        pass_hash = generate_password_hash(DEMO_PASSWORD)

        # 1. Seed Categories
        print("\n[1/7] Seeding Categories...")
        cat_coll = CategoryModel.collection()
        cat_coll.create_index("slug", unique=True)
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
                cat_coll.insert_one(doc)
        print(f"[OK] Categories ready ({len(INITIAL_CATEGORIES)} categories).")

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

        # 3. Seed Marketplace Products (INR prices, category_id = slug)
        print("\n[3/7] Seeding Marketplace Products (INR)...")
        prod_coll = ProductModel.collection()

        demo_products = [
            # ── TEXTBOOKS (7 items) ──
            {"title": "Engineering Mathematics by B.S. Grewal", "description": "44th edition. Essential for all engineering branches. Clean pages with no markings.", "price": 450, "category_id": "textbooks", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Data Structures and Algorithms in Java", "description": "Goodrich & Tamassia. Trees, graphs, sorting, dynamic programming.", "price": 380, "category_id": "textbooks", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Operating System Concepts (Silberschatz 10th Ed)", "description": "The dinosaur book! Required for CS302.", "price": 550, "category_id": "textbooks", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "Database Management Systems (Ramakrishnan & Gehrke)", "description": "SQL, relational algebra, normalization, query optimization.", "price": 320, "category_id": "textbooks", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "Computer Networks by Tanenbaum (5th Edition)", "description": "TCP/IP, routing algorithms, wireless networks, security.", "price": 480, "category_id": "textbooks", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Let Us Python by Yashavant Kanetkar", "description": "Introduction to Python with exercises. Barely used.", "price": 280, "category_id": "textbooks", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1526379095098-d400fd0bf935?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "Discrete Mathematics by Kenneth Rosen", "description": "7th edition. Logic, set theory, combinatorics, graph theory.", "price": 350, "category_id": "textbooks", "condition": "FAIR", "images": ["https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},

            # ── SCIENTIFIC CALCULATORS (3 items) ──
            {"title": "Casio FX-991EX ClassWiz Scientific Calculator", "description": "552 functions, high resolution LCD, QR code display.", "price": 1200, "category_id": "scientific-calculators", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1611125832047-1d7ad1e8e49d?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Casio FX-82MS 2nd Gen Scientific Calculator", "description": "240 functions. University exam approved.", "price": 700, "category_id": "scientific-calculators", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1594980596870-8aa52a78d8cd?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "Texas Instruments TI-84 Plus CE Graphing Calculator", "description": "Color display, USB cable, protective case. For calculus & stats.", "price": 2200, "category_id": "scientific-calculators", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1564466809058-bf4114d55352?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},

            # ── ELECTRONICS (5 items) ──
            {"title": "Arduino Uno R3 Starter Kit with Components", "description": "Complete kit: Uno board, breadboard, sensors, LCD display.", "price": 1800, "category_id": "electronics", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1553406830-ef2513450d76?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Electronics Lab Breadboard & Component Set", "description": "Jumper wires, capacitors, transistors, 7400 series ICs.", "price": 1200, "category_id": "electronics", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "Anker 7-in-1 USB-C Hub Adapter", "description": "HDMI 4K, 100W PD, SD reader, 2x USB 3.0.", "price": 1500, "category_id": "electronics", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1616440342230-016f1082531d?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Logitech K380 Multi-Device Wireless Keyboard", "description": "Bluetooth, connect 3 devices simultaneously.", "price": 1800, "category_id": "electronics", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "SanDisk 1TB External USB 3.2 Portable SSD", "description": "Read speeds up to 800MB/s. For backups and VMs.", "price": 5500, "category_id": "electronics", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},

            # ── LAPTOPS & COMPUTERS (3 items) ──
            {"title": "Lenovo ThinkPad E14 (i5, 16GB RAM, 512GB SSD)", "description": "1080p IPS, long battery. Great for coding.", "price": 32000, "category_id": "laptops-computers", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Dell 24-inch UltraSharp Full HD Monitor", "description": "IPS, adjustable stand, HDMI & DisplayPort.", "price": 8500, "category_id": "laptops-computers", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "HP Pavilion 15 Laptop (Ryzen 5, 8GB, 256GB)", "description": "Reserved for campus buyer. Includes charger.", "price": 25000, "category_id": "laptops-computers", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80"], "status": "RESERVED", "seller_id": seller1_id},

            # ── BICYCLES (2 items) ──
            {"title": "Hero Sprint Hybrid Campus Bicycle", "description": "21 speeds, front basket, U-lock included.", "price": 5500, "category_id": "bicycles", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "Firefox Road Runner 26T Mountain Bicycle", "description": "Front suspension, disc brakes, 21-gear shimano.", "price": 8000, "category_id": "bicycles", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},

            # ── LAB EQUIPMENT (2 items) ──
            {"title": "Chemistry Lab Coat & Safety Goggles Set", "description": "White cotton coat (Size M), anti-fog goggles.", "price": 650, "category_id": "lab-equipment", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Physics Optics Kit (Prisms, Lenses & Laser)", "description": "Glass prisms, lenses, laser pointer for PHY201.", "price": 1100, "category_id": "lab-equipment", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1507668077129-56e32842fceb?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},

            # ── HOSTEL ESSENTIALS (4 items) ──
            {"title": "Adjustable LED Study Desk Lamp (USB Powered)", "description": "3 brightness modes, USB charging port.", "price": 650, "category_id": "hostel-essentials", "condition": "LIKE_NEW", "images": ["https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "Wildcraft 30L Campus Backpack", "description": "Padded laptop sleeve, rain cover, ergonomic straps.", "price": 1200, "category_id": "hostel-essentials", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80"], "status": "RESERVED", "seller_id": seller1_id},
            {"title": "Portable Desk Fan (3-Speed, Quiet Motor)", "description": "USB powered, ideal for hostel room.", "price": 450, "category_id": "hostel-essentials", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1618941723380-496e5797f743?auto=format&fit=crop&w=600&q=80"], "status": "RESERVED", "seller_id": seller2_id},
            {"title": "6-Socket Extension Board with Surge Protector", "description": "ISI certified, 2-meter cord.", "price": 350, "category_id": "hostel-essentials", "condition": "NEW", "images": ["https://images.unsplash.com/photo-1544085311-11a028465b03?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},

            # ── STATIONERY (2 items) ──
            {"title": "Mechanical Drawing Drafting Set (Rotring)", "description": "Compass, divider, protractor, set squares.", "price": 800, "category_id": "stationery", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "A3 Drawing Board with T-Square", "description": "Wooden A3 board, adjustable T-square, 2 French curves.", "price": 600, "category_id": "stationery", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1452587925148-ce544e77e70d?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},

            # ── SPORTS EQUIPMENT (3 items) ──
            {"title": "Yonex Nanoray Light Badminton Racket", "description": "Carbon frame, grip tape, 6 shuttlecocks.", "price": 1500, "category_id": "sports-equipment", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller1_id},
            {"title": "Nivia Cross World Football (Size 5)", "description": "Hand-stitched, holds air perfectly.", "price": 650, "category_id": "sports-equipment", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1614632537197-38a17061c2bd?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},
            {"title": "SG Cricket Bat (Kashmir Willow, Full Size)", "description": "English handle, used one season.", "price": 1800, "category_id": "sports-equipment", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&w=600&q=80"], "status": "RESERVED", "seller_id": seller1_id},

            # ── ACCESSORIES (1 item) ──
            {"title": "boAt Rockerz 450 Wireless Headphones", "description": "Bluetooth 5.0, 15hr battery, foldable.", "price": 900, "category_id": "accessories", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80"], "status": "ACTIVE", "seller_id": seller2_id},

            # ── SOLD Products (2 items) ──
            {"title": "Digital Multimeter (Auto-Ranging)", "description": "Sold to engineering student.", "price": 850, "category_id": "electronics", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80"], "status": "SOLD", "seller_id": seller2_id},
            {"title": "Introduction to Algorithms (CLRS 3rd Edition)", "description": "Sold to CS junior.", "price": 600, "category_id": "textbooks", "condition": "GOOD", "images": ["https://images.unsplash.com/photo-1589998059171-988d887df646?auto=format&fit=crop&w=600&q=80"], "status": "SOLD", "seller_id": seller1_id},

            # ── REMOVED Products (1 item) ──
            {"title": "Suspicious Spam Listing (Flagged)", "description": "Flagged for admin moderation demo.", "price": 99999, "category_id": "accessories", "condition": "POOR", "images": ["https://images.unsplash.com/photo-1584824486509-112e4181ff6b?auto=format&fit=crop&w=600&q=80"], "status": "REMOVED", "seller_id": seller1_id},
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
        calc_id = prod_map.get("Texas Instruments TI-84 Plus CE Graphing Calculator")
        laptop_id = prod_map.get("Lenovo ThinkPad E14 (i5, 16GB RAM, 512GB SSD)")
        bike_id = prod_map.get("Hero Sprint Hybrid Campus Bicycle")

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

        mm_id = prod_map.get("Digital Multimeter (Auto-Ranging)")
        if mm_id:
            req_doc = req_coll.find_one({"product_id": mm_id, "buyer_id": buyer1_id})
            if not req_doc:
                res = req_coll.insert_one({
                    "product_id": mm_id,
                    "buyer_id": buyer1_id,
                    "seller_id": seller2_id,
                    "message": "Hi! Can I pick this up from the EE building tomorrow?",
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
                    "comment": "Very helpful seller! Multimeter was clean and fully tested. Quick campus meetup.",
                    "created_at": now,
                })

        print("[OK] Purchase requests & transaction history seeded.")

        # 7. Seed Admin Reports
        print("\n[7/7] Seeding Admin Moderation Reports...")
        rep_coll = ReportModel.collection()
        spam_id = prod_map.get("Suspicious Spam Listing (Flagged)")
        if spam_id and not rep_coll.find_one({"target_id": spam_id}):
            rep_coll.insert_one({
                "reporter_id": buyer1_id,
                "target_type": "PRODUCT",
                "target_id": spam_id,
                "reason": "Spam or misleading price",
                "description": "Listing price is ₹99,999 — abnormally high and appears to be spam.",
                "status": "OPEN",
                "created_at": now,
                "updated_at": now,
            })

        print("[OK] Admin reports seeded.")

        print("\n==================================================")
        print("  DEMO SEED COMPLETE — ALL DATA READY FOR DEMO!    ")
        print("==================================================")


if __name__ == "__main__":
    seed_demo_data()
