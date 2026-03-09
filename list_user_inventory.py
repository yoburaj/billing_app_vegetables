import sys
import os
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User
from app.models.inventory import Inventory
from app.models.vegetable import Vegetable

# Ensure we can import from app
sys.path.append(os.getcwd())

def list_user_inventory(username):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"Error: User '{username}' not found.")
            # List all users to help the user
            users = db.query(User).all()
            if users:
                print("Available users:")
                for u in users:
                    print(f"- {u.username}")
            return

        print(f"Inventory for user: {user.username} (ID: {user.id})")
        
        inventory_items = db.query(Inventory).filter(Inventory.user_id == user.id).all()
        
        if not inventory_items:
            print("No items found in inventory for this user.")
            return

        print(f"{'ID':<5} {'Name':<25} {'Tamil Name':<20} {'Tanglish':<20} {'Stock':<10} {'Price':<10}")
        print("-" * 95)
        
        for item in inventory_items:
            veg = item.vegetable
            if veg:
                print(f"{veg.id:<5} {veg.name:<25} {veg.tamil_name:<20} {veg.tanglish_name or 'N/A':<20} {item.stock_kg:<10} {item.price_per_kg:<10}")
            else:
                print(f"Unknown vegetable ID: {item.vegetable_id}")

    finally:
        db.close()

if __name__ == "__main__":
    target_user = "yoburaj"
    if len(sys.argv) > 1:
        target_user = sys.argv[1]
    list_user_inventory(target_user)
