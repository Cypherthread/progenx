#!/usr/bin/env python3
"""
Promote a user to admin tier. CLI-only, no API exposure.

Usage:
  python scripts/make_admin.py your@email.com

This sets user.tier = "admin" directly in the database.
Admin tier gets: unlimited designs, Claude AI, all validation, no rate limits.

Security: This script requires direct access to the server/database.
There is no API endpoint for this. Nobody can become admin remotely.
"""

import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import User


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/make_admin.py your@email.com")
        sys.exit(1)

    email = sys.argv[1]

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User not found: {email}")
            print("Make sure you've signed up first.")
            sys.exit(1)

        if user.tier == "admin":
            print(f"User {email} is already admin.")
            return

        old_tier = user.tier
        user.tier = "admin"
        db.commit()

        print(f"Promoted {email}: {old_tier} → admin")
        print("Unlimited designs, Claude AI, all features enabled.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
