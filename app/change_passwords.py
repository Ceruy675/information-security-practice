from getpass import getpass

from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def change_password(email):
    with SessionLocal() as db:
        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:
            print(f"User {email} not found")
            return

        password = getpass(
            f"New password for {email}: "
        )

        if not 8 <= len(password.encode("utf-8")) <= 72:
            print("Password must be 8-72 bytes")
            return

        confirm = getpass("Confirm password: ")

        if password != confirm:
            print("Passwords do not match")
            return

        user.hashed_password = hash_password(password)
        db.commit()

        print(f"Password updated: {email}")


if __name__ == "__main__":
    change_password("teacher@example.com")
    change_password("admin@example.com")
