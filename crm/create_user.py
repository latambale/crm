# create_user.py
from app.db import SessionLocal
from app.models import User

db = SessionLocal()

new_user = User(
    username="saurabh",
    email="saurabh@example.com",
    password="Latambale@1999"  # Ideally hash it
)

db.add(new_user)
db.commit()
db.close()