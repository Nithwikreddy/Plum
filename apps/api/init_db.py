#!/usr/bin/env python
"""
Database initialization and seeding script
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import create_app
from app.db_models import db, Member


def init_database():
    """Initialize database with test data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Seed test members
        print("Seeding test members...")
        test_members = [
            ("EMP001", "Ramesh Kumar", "2024-09-01"),
            ("EMP002", "Priya Singh", "2024-09-01"),
            ("EMP003", "Amit Patel", "2024-09-01"),
            ("EMP004", "Neha Verma", "2024-09-01"),
            ("EMP005", "Rajesh Kumar", "2024-09-01"),
            ("EMP006", "Deepak Sharma", "2024-09-01"),
            ("EMP007", "Sanjay Gupta", "2024-09-01"),
            ("EMP008", "Vikram Reddy", "2024-09-01"),
            ("EMP009", "Arjun Singh", "2024-09-01"),
        ]
        
        for member_id, name, join_date in test_members:
            # Check if member exists
            member = Member.query.get(member_id)
            if not member:
                member = Member(
                    id=member_id,
                    name=name,
                    join_date=datetime.strptime(join_date, "%Y-%m-%d"),
                    is_active=True
                )
                db.session.add(member)
                print(f"  Added member: {member_id} ({name})")
            else:
                print(f"  Member already exists: {member_id}")
        
        db.session.commit()
        print("\nDatabase initialization complete!")
        print(f"Total members: {Member.query.count()}")


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
