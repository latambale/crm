# create_user.py
from app.db import SessionLocal
from app.models import User
from sqlalchemy import func

db = SessionLocal()

agents = db.query(User.id, User.username, User.status).filter(
    func.lower(User.role) == "agent"
).all()

for a in agents:
    print(f"ID: {a.id}, Username: {a.username}, Status: '{a.status}'")


db.close()
