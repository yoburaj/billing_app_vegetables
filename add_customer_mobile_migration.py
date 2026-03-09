from app.database.database import engine
from sqlalchemy import text
import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

def add_column():
    print("Attempting to add 'customer_mobile' column to 'bills' table...")
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE bills ADD COLUMN IF NOT EXISTS customer_mobile VARCHAR(15);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_bills_customer_mobile ON bills(customer_mobile);"))
            conn.commit()
            print("Migration successful: Added customer_mobile column and index to bills table.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    add_column()
