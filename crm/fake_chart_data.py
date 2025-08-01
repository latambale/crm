# fake_lead_data.py
from datetime import datetime, timedelta
from app.db import SessionLocal
from app.models import Lead

db = SessionLocal()

# Get a few leads to update
leads = db.query(Lead).limit(10).all()

for i, lead in enumerate(leads):
    lead.status = "converted"
    lead.updated_at = datetime.utcnow() - timedelta(days=i)
    lead.property_type = "1BHK" if i % 2 == 0 else "2BHK"

db.commit()
print("Leads updated with fake converted data.")
