from sqlalchemy import text
from app.database.database import engine, Base
from app.models.user import User
from app.models.vegetable import Vegetable
from app.models.inventory import Inventory
from app.models.bill import Bill, BillItem
from app.models.usage import VegetableUsage
from app.models.customer import Customer
from app.utils.seed_vegetables import seed_vegetables
from app.database.database import SessionLocal
from app.models.user import User, UserRole
from app.core.auth import get_password_hash

def reset_database():
    print("Dropping all tables...")
    # Using raw SQL to drop everything for PostgreSQL to handle dependencies
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS bill_items CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS bills CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS inventory CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS vegetable_usage CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS vegetables CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS customers CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.execute(text("DROP TYPE IF EXISTS userrole;"))
        conn.commit()
    
    print("Creating all tables from scratch...")
    Base.metadata.create_all(bind=engine)
    
    print("Seeding vegetables and admin...")
    db = SessionLocal()
    try:
        seed_vegetables(db)
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        print("Success! Database reset and admin created (admin/admin123).")
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
