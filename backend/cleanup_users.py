import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models.logging_models import User

def cleanup_users():
    db = SessionLocal()
    try:
        # Delete all users except maina
        # Using ilike in case of case sensitivity or slightly different domain
        deleted_count = db.query(User).filter(~User.email.ilike("maina%")).delete(synchronize_session=False)
        db.commit()
        print(f"Deleted {deleted_count} user(s).")
        
        # Verify remaining users
        remaining = db.query(User).all()
        print("Remaining users:")
        for user in remaining:
            print(f"- {user.email}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_users()
