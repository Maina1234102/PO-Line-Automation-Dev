import sys
import os

# Add the parent directory to sys.path to allow importing from backend.app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal
from backend.app.models.logging_models import User

users_to_add = [
    "jokash.panigrahi@inspiraenterprise.com",
    "akhilesh.vishwasrao@inspiraenterprise.com",
    "Dinesh@inspiraenterprise.com",
    "jyoti.gaikwad@inspiraenterprise.com",
    "monal.jaigude@inspiraenterprise.com",
    "parikshit.sanap@inspiraenterprise.com",
    "srithar.seshan@inspiraenterprise.com",
    "dewendra.thakur@inspiraenterprise.com",
    "esai.nadar@inspiraenterprise.com",
    "narendra.sonawane@inspiraenterprise.com"
]

password = "Welcome@123"

def add_users():
    db = SessionLocal()
    try:
        for email in users_to_add:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"User {email} already exists. Skipping.")
                continue
            
            new_user = User(
                email=email,
                password=password,
                is_active=True
            )
            db.add(new_user)
            print(f"Added user: {email}")
        
        db.commit()
        print("Successfully added all users.")
    except Exception as e:
        db.rollback()
        print(f"Error adding users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_users()
