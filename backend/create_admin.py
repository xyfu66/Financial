"""
Admin user creation script for Personal Financial Management System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User, UserDetail
from app.core.database import SessionLocal
from app.core.security import get_password_hash
import getpass

def create_admin_user():
    """Create an admin user for the system"""
    
    print("=== Personal Financial Management System ===")
    print("Admin User Creation Script")
    print("=" * 45)
    
    # Get user input
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email: ").strip()
    
    if not email:
        print("Error: Email is required")
        return False
    
    # Get password with confirmation
    while True:
        password = getpass.getpass("Enter admin password: ")
        if len(password) < 8:
            print("Error: Password must be at least 8 characters long")
            continue
        
        confirm_password = getpass.getpass("Confirm admin password: ")
        if password != confirm_password:
            print("Error: Passwords do not match")
            continue
        break
    
    # Get user details
    first_name = input("Enter first name (default: 管理者): ").strip() or "管理者"
    last_name = input("Enter last name (default: システム): ").strip() or "システム"
    
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"Error: User with username '{username}' or email '{email}' already exists")
            return False
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            role='super_admin',
            is_active=True
        )
        
        db.add(admin_user)
        db.flush()  # Get the user_id
        
        # Create user detail
        user_detail = UserDetail(
            user_id=admin_user.user_id,
            first_name=first_name,
            last_name=last_name
        )
        
        db.add(user_detail)
        db.commit()
        
        print("\n" + "=" * 45)
        print("✅ Admin user created successfully!")
        print("=" * 45)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Role: Super Admin")
        print(f"Name: {last_name} {first_name}")
        print("=" * 45)
        print("\nYou can now login to the system with these credentials.")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()

def main():
    """Main function"""
    try:
        success = create_admin_user()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()