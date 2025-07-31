# debug_check.py
from app.db import SessionLocal
from app.models import Lead

db = SessionLocal()
leads = db.query(Lead).all()
print(f"Total leads: {len(leads)}")
for lead in leads:
    print(lead.name, lead.phone, lead.created_at)
db.close()
