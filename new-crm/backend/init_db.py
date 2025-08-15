from database import Base, engine, SessionLocal
from models import User, Lead, Project  # add Lead here

db = SessionLocal()

Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)

from passlib.hash import bcrypt

# Create users if not already done
db.add_all([
    User(phone="0000000000", password=bcrypt.hash("admin"), role="admin"),
    User(phone="1111111111", password=bcrypt.hash("manager"), role="manager"),
    User(phone="2222222222", password=bcrypt.hash("tele"), role="telecaller"),
    Project(name="Urban Greens", location="Wakad", property_type="1BHK", budget_range="50L-60L",
            description="Spacious flats with modern amenities"),
    Project(name="Skyline Towers", location="Baner", property_type="2BHK", budget_range="60L-70L",
            description="Premium tower with club house"),
    Project(name="Gosavi Towers", location="Balewadi", property_type="3BHK", budget_range="1.15-2.25",
            description="Premium tower with club house"),

])
db.commit()

# Add leads for telecaller
db.add_all([
    Lead(name="Ravi Arjun", phone="9012345678", status="fresh", assigned_to=3),
    Lead(name="Anjali Sanu", phone="9123456789", status="fresh", assigned_to=3),
    Lead(name="Pooja Singh", phone="9234567890", status="fresh", assigned_to=3),
])

db.commit()
db.close()