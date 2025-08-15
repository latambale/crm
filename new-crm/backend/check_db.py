from database import SessionLocal
from models import User, Lead, LeadDetails, Project, SiteVisit

def check_db_contents():
    session = SessionLocal()

    print("📱 Users:")
    for u in session.query(User).all():
        print(f"  ID: {u.id} | Phone: {u.phone} | Role: {u.role}")

    print("\n📞 Leads:")
    for l in session.query(Lead).all():
        print(f"  ID: {l.id} | Name: {l.name} | Phone: {l.phone} | Status: {l.status} | Assigned To: {l.assigned_to}")

    print("\n📝 Lead Details:")
    for d in session.query(LeadDetails).all():
        print(f"  Lead ID: {d.lead_id} | Looking For: {d.looking_for} | Budget: {d.budget} | Location: {d.location_preference}")

    print("\n🏢 Projects:")
    for p in session.query(Project).all():
        print(f"  ID: {p.id} | Name: {p.name} | Type: {p.property_type} | Budget: {p.budget_range} | Location: {p.location}")

    print("\n📍 Site Visits:")
    for s in session.query(SiteVisit).all():
        print(f"  Lead ID: {s.lead_id} | Project ID: {s.project_id} | Date: {s.date} | Notes: {s.notes}")

    session.close()

if __name__ == "__main__":
    check_db_contents()
