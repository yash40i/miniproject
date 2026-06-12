import sys
from src.database import SessionLocal, User, init_db
from src.auth import hash_password

try:
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    print("Testing User model...")
    db = SessionLocal()
    test_user = User(email="test@test.com", hashed_password=hash_password("test123"), full_name="Test User")
    db.add(test_user)
    db.commit()
    print("✓ User created successfully")
    
    # Query the user
    user = db.query(User).filter(User.email == "test@test.com").first()
    print(f"✓ User retrieved: {user.email}, ID: {user.id}")
    db.close()
    print("✓ All tests passed")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
