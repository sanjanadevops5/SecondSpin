import os
import sys

# Add the parent directory to the path so we can import backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models.product import ProductModel
from backend.models.wishlist import WishlistModel
from backend.models.purchase_request import PurchaseRequestModel

def setup_indexes():
    app = create_app()
    with app.app_context():
        print("Setting up indexes for MongoDB collections...")
        
        try:
            ProductModel.setup_indexes()
            print("[OK] Product indexes created.")
        except Exception as e:
            print(f"[FAIL] Failed to create Product indexes: {e}")
            
        try:
            WishlistModel.setup_indexes()
            print("[OK] Wishlist indexes created.")
        except Exception as e:
            print(f"[FAIL] Failed to create Wishlist indexes: {e}")
            
        try:
            PurchaseRequestModel.setup_indexes()
            print("[OK] Purchase Request indexes created.")
        except Exception as e:
            print(f"[FAIL] Failed to create Purchase Request indexes: {e}")
            
        print("Done.")

if __name__ == '__main__':
    setup_indexes()
