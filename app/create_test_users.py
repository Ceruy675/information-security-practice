from getpass import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def create_user(email, role):
    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(User.email == email)
        )

        if existing:
            print(f"User {email} already exists")
            return

        password = getpass(f"Password for {email}: ")

        if not 8 <= len(password.encode("utf-8")) <= 72:
            print("Password must be 8-72 bytes")
            return

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=role
        )

        db.add(user)
        db.commit()
        print(f"Created {role}: {email}")


if __name__ == "__main__":
    create_user("teacher@example.com", "teacher")
    create_user("admin@example.com", "admin")
