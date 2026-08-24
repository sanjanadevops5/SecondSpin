import os
import sys
import datetime

# Add the backend directory to the path so we can import from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models.category import CategoryModel

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
    {"name": "Other", "slug": "other"}
]

def seed_categories():
    app = create_app()
    with app.app_context():
        collection = CategoryModel.collection()
        
        # Create an index on slug for fast lookups and uniqueness
        collection.create_index("slug", unique=True)
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        print("Starting category seed...")
        
        for cat_data in INITIAL_CATEGORIES:
            existing = collection.find_one({"slug": cat_data["slug"]})
            
            if not existing:
                cat_doc = {
                    "name": cat_data["name"],
                    "slug": cat_data["slug"],
                    "is_active": True,
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                    "updated_at": datetime.datetime.now(datetime.timezone.utc)
                }
                collection.insert_one(cat_doc)
                created_count += 1
                print(f"Created: {cat_data['name']}")
            else:
                # If name changed, we could update it, or just skip
                if existing.get("name") != cat_data["name"]:
                    collection.update_one(
                        {"_id": existing["_id"]},
                        {"$set": {
                            "name": cat_data["name"],
                            "updated_at": datetime.datetime.now(datetime.timezone.utc)
                        }}
                    )
                    updated_count += 1
                    print(f"Updated: {cat_data['name']}")
                else:
                    skipped_count += 1
                    
        print("\nCategory seed complete:")
        print(f"Created: {created_count}")
        print(f"Updated: {updated_count}")
        print(f"Skipped: {skipped_count}")

if __name__ == "__main__":
    seed_categories()
