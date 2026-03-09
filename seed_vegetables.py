import sys
import os
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models.user import User
from app.models.vegetable import Vegetable
from app.models.inventory import Inventory

# Ensure we can import from app
sys.path.append(os.getcwd())

def seed_vegetables(username):
    db = SessionLocal()
    try:
        # Get the target user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"Error: User '{username}' not found. Please create the user first.")
            return

        items = [
            {"tamil": "பச்சைமிளகாய்", "english": "Green Chilli", "tanglish": "Pachai Milagai", "category": "Vegetables"},
            {"tamil": "தக்காளி", "english": "Tomato", "tanglish": "Thakkali", "category": "Vegetables"},
            {"tamil": "வெங்காயம்", "english": "Onion", "tanglish": "Vengayam", "category": "Vegetables"},
            {"tamil": "உருளைக்கிழங்கு", "english": "Potato", "tanglish": "Urulaikizhangu", "category": "Vegetables"},
            {"tamil": "கேரட்", "english": "Carrot", "tanglish": "Carrot", "category": "Vegetables"},
            {"tamil": "பீன்ஸ்", "english": "Beans", "tanglish": "Beans", "category": "Vegetables"},
            {"tamil": "அவரைக்காய்", "english": "Broad Beans", "tanglish": "Avaraikkai", "category": "Vegetables"},
            {"tamil": "முள்ளங்கி", "english": "Radish", "tanglish": "Mullangi", "category": "Vegetables"},
            {"tamil": "இஞ்சி", "english": "Ginger", "tanglish": "Inji", "category": "Vegetables"},
            {"tamil": "பூண்டு", "english": "Garlic", "tanglish": "Poondu", "category": "Vegetables"},
            {"tamil": "கத்திரிக்காய்", "english": "Brinjal (Eggplant)", "tanglish": "Kathirikkai", "category": "Vegetables"},
            {"tamil": "முருங்கைக்காய்", "english": "Drumstick", "tanglish": "Murungaikkai", "category": "Vegetables"},
            {"tamil": "மாங்காய்", "english": "Raw Mango", "tanglish": "Maangai", "category": "Vegetables"},
            {"tamil": "கோஸ்", "english": "Cabbage", "tanglish": "Kos", "category": "Vegetables"},
            {"tamil": "காலிப்ளவர்", "english": "Cauliflower", "tanglish": "Cauliflower", "category": "Vegetables"},
            {"tamil": "சுரைக்காய்", "english": "Bottle Gourd", "tanglish": "Suraikkai", "category": "Vegetables"},
            {"tamil": "புடலங்காய்", "english": "Snake Gourd", "tanglish": "Pudalangai", "category": "Vegetables"},
            {"tamil": "பாகற்காய்", "english": "Bitter Gourd", "tanglish": "Pavakkai", "category": "Vegetables"},
            {"tamil": "சேனைக்கிழங்கு", "english": "Elephant Yam", "tanglish": "Senaikizhangu", "category": "Vegetables"},
            {"tamil": "பீட்ரூட்", "english": "Beetroot", "tanglish": "Beetroot", "category": "Vegetables"},
            {"tamil": "கீரை", "english": "Spinach (Greens)", "tanglish": "Keerai", "category": "Leafy"},
            {"tamil": "கொத்தமல்லி", "english": "Coriander Leaves", "tanglish": "Kothamalli", "category": "Leafy"},
            {"tamil": "புதினா", "english": "Mint", "tanglish": "Pudina", "category": "Leafy"},
            {"tamil": "சோளம்", "english": "Corn", "tanglish": "Cholam", "category": "Vegetables"},
            {"tamil": "பட்டாணி", "english": "Peas", "tanglish": "Pattani", "category": "Vegetables"},
            {"tamil": "சுண்டைக்காய்", "english": "Turkey Berry", "tanglish": "Sundakkai", "category": "Vegetables"},
            {"tamil": "பீர்க்கங்காய்", "english": "Ridge Gourd", "tanglish": "Peerkangai", "category": "Vegetables"},
            {"tamil": "சௌசௌ", "english": "Chayote", "tanglish": "Chow Chow", "category": "Vegetables"},
            {"tamil": "வாழைக்காய்", "english": "Raw Banana", "tanglish": "Vazhaikkai", "category": "Vegetables"},
            {"tamil": "வெண்டைக்காய்", "english": "Lady’s Finger (Okra)", "tanglish": "Vendakkai", "category": "Vegetables"},
            {"tamil": "கருணைக்கிழங்கு", "english": "Taro Root", "tanglish": "Karunaikizhangu", "category": "Vegetables"},
            {"tamil": "கப்பிக்கிழங்கு", "english": "Tapioca", "tanglish": "Kappikizhangu", "category": "Vegetables"},
            {"tamil": "பரங்கிக்காய்", "english": "Pumpkin", "tanglish": "Parangikkai", "category": "Vegetables"},
            {"tamil": "கத்தரிக்காய் (நாட்டு)", "english": "Country Brinjal", "tanglish": "Nattu Kathirikkai", "category": "Vegetables"},
            {"tamil": "பச்சைப்பட்டாணி", "english": "Green Peas", "tanglish": "Pachai Pattani", "category": "Vegetables"},
            {"tamil": "வெள்ளரிக்காய்", "english": "Cucumber", "tanglish": "Vellarikkai", "category": "Vegetables"},
            {"tamil": "குடமிளகாய்", "english": "Capsicum", "tanglish": "Kudamilagai", "category": "Vegetables"},
            {"tamil": "முள்ளுக்கீரை", "english": "Amaranthus Greens", "tanglish": "Mullukeerai", "category": "Leafy"},
            {"tamil": "தண்டுக்கீரை", "english": "Stem Amaranth", "tanglish": "Thandukeerai", "category": "Leafy"},
            {"tamil": "மணத்தக்காளி", "english": "Black Nightshade", "tanglish": "Manathakkali", "category": "Leafy"},
        ]

        print(f"Seeding {len(items)} items for user '{user.username}'...")

        for item in items:
            # Check/Create Vegetable in master list
            veg = db.query(Vegetable).filter(Vegetable.name == item["english"]).first()
            if not veg:
                veg = Vegetable(
                    name=item["english"],
                    tamil_name=item["tamil"],
                    tanglish_name=item["tanglish"],
                    category=item["category"],
                    price_per_kg=0.0,
                    retail_price=0.0,
                    wholesale_price=0.0
                )
                db.add(veg)
                db.flush()
            else:
                veg.tamil_name = item["tamil"]
                veg.tanglish_name = item["tanglish"]
                veg.category = item["category"]

            # Add to user inventory
            inv = db.query(Inventory).filter(
                Inventory.user_id == user.id,
                Inventory.vegetable_id == veg.id
            ).first()

            if not inv:
                inv = Inventory(
                    user_id=user.id,
                    vegetable_id=veg.id,
                    price_per_kg=0.0,
                    retail_price=0.0,
                    wholesale_price=0.0,
                    stock_kg=100.0
                )
                db.add(inv)
                
        db.commit()
        print(f"Success! Vegetables seeded for {user.username}.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    target_user = "admin"
    if len(sys.argv) > 1:
        target_user = sys.argv[1]
    seed_vegetables(target_user)
