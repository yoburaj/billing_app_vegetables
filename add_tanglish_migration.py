from app.database.database import engine
from sqlalchemy import text
import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

def add_column():
    print("Attempting to add 'tanglish_name' column to 'vegetables' table...")
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE vegetables ADD COLUMN IF NOT EXISTS tanglish_name VARCHAR;"))
            conn.commit()
            print("Migration successful: Added tanglish_name column.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    add_column()
