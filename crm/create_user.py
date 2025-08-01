# create_user.py
from app.db import SessionLocal
from app.models import User

db = SessionLocal()

new_user = User(
    username="agent4",
    email="agent4@example.com",
    password="agent",
    role="agent"
)

db.add(new_user)
db.commit()
db.close()