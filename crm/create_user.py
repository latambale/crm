# create_user.py
from app.db import SessionLocal
from app.models import User

db = SessionLocal()

users = [
    {"username": "agent1", "email": "agent1@example.com", "password": "agent", "role": "agent", "status": "active"},
    {"username": "agent2", "email": "agent2@example.com", "password": "agent", "role": "agent", "status": "active"},
    {"username": "agent3", "email": "agent3@example.com", "password": "agent", "role": "agent", "status": "inactive"},
    {"username": "agent4", "email": "agent4@example.com", "password": "agent", "role": "agent", "status": "active"},
    {"username": "admin",  "email": "admin@example.com",  "password": "admin", "role": "admin", "status": "active"},
]

for user_data in users:
    user = User(**user_data)
    db.add(user)

db.commit()
db.close()
