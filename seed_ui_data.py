import sys
import os
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models.user import User
from app.models.vegetable import Vegetable
from app.models.inventory import Inventory

# Ensure we can import from app
sys.path.append(os.getcwd())

def seed_ui_inventory():
    db = SessionLocal()
    try:
        # 1. Get the admin user to assign inventory to
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("Error: Admin user not found. Please run reset_db.py first.")
            return

        payload = {
            "items": [
                {
                    "name": "Tomato",
                    "tamilName": "தக்காளி",
                    "category": "Root Veggies",
                    "price": 32.0,
                    "image": "https://images.unsplash.com/photo-1518977676601-b53f02bad675?q=80&w=400"
                },
                {
                    "name": "Onion",
                    "tamilName": "வெங்காயம்",
                    "category": "Root Veggies",
                    "price": 45.0,
                    "image": "https://images.unsplash.com/photo-1508747703725-719777637510?q=80&w=400"
                },
                {
                    "name": "Carrot",
                    "tamilName": "கேரட்",
                    "category": "Root Veggies",
                    "price": 58.0,
                    "image": "https://images.unsplash.com/photo-1590865101275-4d40089e9f29?q=80&w=400"
                },
                {
                    "name": "Brinjal",
                    "tamilName": "கத்தரிக்காய்",
                    "category": "Others",
                    "price": 40.0,
                    "image": "https://images.unsplash.com/photo-1533475765664-88404ee6d926?q=80&w=400"
                }
            ]
        }

        print(f"Seeding {len(payload['items'])} items for user '{admin.username}'...")

        for item in payload["items"]:
            # Check/Create Vegetable
            veg = db.query(Vegetable).filter(Vegetable.name == item["name"]).first()
            if not veg:
                veg = Vegetable(
                    name=item["name"],
                    tamil_name=item["tamilName"],
                    category=item["category"],
                    image_url=item["image"],
                    price_per_kg=item["price"],
                    retail_price=item["price"],
                    wholesale_price=item["price"] * 0.8
                )
                db.add(veg)
                db.flush()
            else:
                # Update existing master info
                veg.tamil_name = item["tamilName"]
                veg.category = item["category"]
                veg.image_url = item["image"]
                veg.price_per_kg = item["price"]

            # Check/Create Inventory for Admin
            inv = db.query(Inventory).filter(
                Inventory.user_id == admin.id,
                Inventory.vegetable_id == veg.id
            ).first()

            if not inv:
                inv = Inventory(
                    user_id=admin.id,
                    vegetable_id=veg.id,
                    price_per_kg=item["price"],
                    retail_price=item["price"],
                    wholesale_price=item["price"] * 0.8,
                    stock_kg=100.0
                )
                db.add(inv)
            else:
                inv.price_per_kg = item["price"]
                inv.retail_price = item["price"]
                inv.wholesale_price = item["price"] * 0.8

        db.commit()
        print("Success! UI vegetables seeded successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_ui_inventory()
