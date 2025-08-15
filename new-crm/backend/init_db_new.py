# scripts/seed_dev_db.py

from datetime import datetime, timedelta, date
import json
import random
import uuid

from passlib.hash import bcrypt

from database import Base, engine, SessionLocal
from models import (
    User,
    Lead,
    LeadDetails,
    Project,
    ProjectInfo,
    SiteVisit,
    # If you added these, you can seed later:
    # Attendance, LiveLocation
)

# -----------------------------
# Helpers
# -----------------------------

def rand_phone(start=9000000000):
    # Generate unique-ish 10-digit phone numbers
    return str(start + random.randint(0, 8_999_999)).zfill(10)

def jdump(obj):
    return json.dumps(obj, ensure_ascii=False)

def pick(seq):
    return random.choice(seq)

def seed_users(db):
    users = [
        # Admins
        User(phone="0000000000", password=bcrypt.hash("admin"), role="admin"),

        # Managers (2)
        User(phone="1111111111", password=bcrypt.hash("manager1"), role="manager"),
        User(phone="1111112222", password=bcrypt.hash("manager2"), role="manager"),

        # Telecallers (3)
        User(phone="2222221111", password=bcrypt.hash("tele1"), role="telecaller"),
        User(phone="2222222222", password=bcrypt.hash("tele2"), role="telecaller"),
        User(phone="2222223333", password=bcrypt.hash("tele3"), role="telecaller"),
    ]
    db.add_all(users)
    db.commit()

    managers = db.query(User).filter(User.role == "manager").all()
    telecallers = db.query(User).filter(User.role == "telecaller").all()

    return {
        "admin": db.query(User).filter(User.role == "admin").first(),
        "managers": managers,
        "telecallers": telecallers,
    }

def seed_projects(db):
    # Rich sample inventory across Pune localities
    projects_seed = [
        {
            "base": dict(
                name="Urban Greens",
                location="Wakad",
                property_type="1BHK,2BHK",
                budget_range="₹50L–₹80L",
                description="Modern township with greens, clubhouse and kids’ play area."
            ),
            "info": dict(
                developer_name="SkyNest Developers",
                experience="10+ years",
                completed_projects="8",
                landmark="Near Phoenix Wakad Mall",
                possession_type="Under Construction",
                total_land="5 acres",
                total_towers="4",
                number_of_floors="18",
                construction_technology="Mivan",
                number_of_amenities="20+",
                types_of_inventory=["1BHK", "2BHK"],
                carpet_area_json=jdump({"1BHK": "420–480", "2BHK": "650–720"}),
                flats_per_floor="4",
                lifts="2 per wing",
            ),
        },
        {
            "base": dict(
                name="Skyline Towers",
                location="Baner",
                property_type="2BHK,3BHK",
                budget_range="₹90L–₹1.6Cr",
                description="Premium tower with infinity pool, co-working lounge."
            ),
            "info": dict(
                developer_name="Beacon Constructions",
                experience="15+ years",
                completed_projects="12",
                landmark="Behind Pancard Club",
                possession_type="Ready to Move",
                total_land="3 acres",
                total_towers="2",
                number_of_floors="22",
                construction_technology="RCC",
                number_of_amenities="25+",
                types_of_inventory=["2BHK", "3BHK"],
                carpet_area_json=jdump({"2BHK": "700–820", "3BHK": "900–1150"}),
                flats_per_floor="3",
                lifts="3 per tower",
            ),
        },
        {
            "base": dict(
                name="Gosavi Towers",
                location="Balewadi",
                property_type="3BHK,4BHK",
                budget_range="₹1.15Cr–₹2.25Cr",
                description="Luxury residences with triple-height lobby and concierge."
            ),
            "info": dict(
                developer_name="Gosavi Realty",
                experience="20+ years",
                completed_projects="18",
                landmark="Opp. Balewadi High Street",
                possession_type="Under Construction",
                total_land="2.5 acres",
                total_towers="3",
                number_of_floors="24",
                construction_technology="Shear Wall",
                number_of_amenities="30+",
                types_of_inventory=["3BHK", "4BHK"],
                carpet_area_json=jdump({"3BHK": "1100–1350", "4BHK": "1450–1750"}),
                flats_per_floor="2",
                lifts="4 per tower",
            ),
        },
        {
            "base": dict(
                name="Blue Orchid",
                location="Hinjewadi",
                property_type="1BHK,2BHK,Studio",
                budget_range="₹40L–₹70L",
                description="IT-park adjacency, ideal for rental yield."
            ),
            "info": dict(
                developer_name="Orchid Group",
                experience="12+ years",
                completed_projects="10",
                landmark="Near Infosys Phase 2",
                possession_type="Under Construction",
                total_land="6 acres",
                total_towers="5",
                number_of_floors="21",
                construction_technology="Aluform",
                number_of_amenities="18+",
                types_of_inventory=["Studio", "1BHK", "2BHK"],
                carpet_area_json=jdump({"Studio": "320–360", "1BHK": "400–460", "2BHK": "600–690"}),
                flats_per_floor="6",
                lifts="3 per wing",
            ),
        },
        {
            "base": dict(
                name="Riverfront Residences",
                location="Kharadi",
                property_type="2BHK,3BHK",
                budget_range="₹85L–₹1.5Cr",
                description="Riverside promenade, large clubhouse and sports courts."
            ),
            "info": dict(
                developer_name="Trident Estates",
                experience="14+ years",
                completed_projects="9",
                landmark="Near EON IT Park",
                possession_type="Under Construction",
                total_land="7 acres",
                total_towers="6",
                number_of_floors="20",
                construction_technology="RCC",
                number_of_amenities="22+",
                types_of_inventory=["2BHK", "3BHK"],
                carpet_area_json=jdump({"2BHK": "680–800", "3BHK": "900–1200"}),
                flats_per_floor="4",
                lifts="2 per wing",
            ),
        },
        {
            "base": dict(
                name="Hillcrest Vista",
                location="Bavdhan",
                property_type="2BHK,3BHK",
                budget_range="₹75L–₹1.35Cr",
                description="Hill-facing apartments with sky-garden decks."
            ),
            "info": dict(
                developer_name="Zen Habitat",
                experience="8+ years",
                completed_projects="5",
                landmark="Near NDA Road",
                possession_type="Ready to Move",
                total_land="4 acres",
                total_towers="3",
                number_of_floors="19",
                construction_technology="RCC",
                number_of_amenities="15+",
                types_of_inventory=["2BHK", "3BHK"],
                carpet_area_json=jdump({"2BHK": "670–760", "3BHK": "880–1050"}),
                flats_per_floor="3",
                lifts="3 per tower",
            ),
        },
        {
            "base": dict(
                name="Cityline Meadows",
                location="Viman Nagar",
                property_type="1BHK,2BHK",
                budget_range="₹60L–₹95L",
                description="Airport connectivity + retail high street inside campus."
            ),
            "info": dict(
                developer_name="Cityline Infra",
                experience="11+ years",
                completed_projects="7",
                landmark="Opp. Phoenix Marketcity",
                possession_type="Under Construction",
                total_land="3.5 acres",
                total_towers="3",
                number_of_floors="18",
                construction_technology="RCC",
                number_of_amenities="16+",
                types_of_inventory=["1BHK", "2BHK"],
                carpet_area_json=jdump({"1BHK": "420–470", "2BHK": "650–740"}),
                flats_per_floor="4",
                lifts="2 per wing",
            ),
        },
        {
            "base": dict(
                name="Park Avenue",
                location="Magarpatta",
                property_type="2BHK,3BHK",
                budget_range="₹95L–₹1.7Cr",
                description="Inside township: schools, hospital, huge central park."
            ),
            "info": dict(
                developer_name="GreenSquare",
                experience="18+ years",
                completed_projects="14",
                landmark="Inside Magarpatta City",
                possession_type="Ready to Move",
                total_land="8 acres",
                total_towers="7",
                number_of_floors="20",
                construction_technology="RCC",
                number_of_amenities="28+",
                types_of_inventory=["2BHK", "3BHK"],
                carpet_area_json=jdump({"2BHK": "720–840", "3BHK": "980–1250"}),
                flats_per_floor="4",
                lifts="3 per tower",
            ),
        },
    ]

    project_ids = []
    for p in projects_seed:
        base = Project(**p["base"])
        db.add(base)
        db.commit()
        db.refresh(base)

        info = ProjectInfo(project_id=base.id, **p["info"])
        # types_of_inventory in your model is comma-separated string; ensure it is so
        if isinstance(info.types_of_inventory, list):
            info.types_of_inventory = ",".join(info.types_of_inventory)
        db.add(info)
        db.commit()

        project_ids.append(base.id)

    return project_ids

def seed_leads(db, telecallers, project_ids):
    # Names + simple preferences
    first_names = ["Ravi", "Anjali", "Pooja", "Rahul", "Sneha", "Amit", "Kiran", "Priya", "Neha", "Sagar",
                   "Lokesh", "Isha", "Varun", "Ameya", "Yash", "Sonia", "Payal", "Rohit", "Mitali", "Rakesh"]
    last_names  = ["Sharma", "Patil", "Joshi", "Khan", "Verma", "Kulkarni", "Deshmukh", "Bhosale", "Rao", "Chavan"]

    locations   = ["Wakad", "Baner", "Balewadi", "Hinjewadi", "Kharadi", "Bavdhan", "Viman Nagar", "Magarpatta"]
    inventory   = ["Studio", "1BHK", "2BHK", "3BHK", "4BHK"]
    budgets     = ["₹40L–₹60L", "₹60L–₹80L", "₹80L–₹1Cr", "₹1Cr–₹1.5Cr", "₹1.5Cr–₹2Cr"]
    possession  = ["1–3 months", "3–6 months", "6–12 months", "Ready to Move"]

    # Stage distribution
    stages_pool = (
        ["fresh"] * 12 +          # 12 fresh
        ["connected"] * 6 +       # 6 connected
        ["warm"] * 5 +            # 5 warm
        ["hot"] * 4 +             # 4 hot
        ["svs"] * 3               # 3 with site visits
    )

    leads_created = []
    seed_batch = f"seed_{str(uuid.uuid4())[:8]}"

    for i in range(30):
        name = f"{pick(first_names)} {pick(last_names)}"
        phone = rand_phone(9300000000 + i * 1000)
        stage = pick(stages_pool)
        status = "fresh" if stage == "fresh" else "in_progress"
        assigned_to = pick(telecallers).id

        lead = Lead(
            name=name,
            phone=phone,
            status=status,
            assigned_to=assigned_to
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        ld = LeadDetails(
            lead_id=lead.id,
            looking_for=pick(inventory),
            budget=pick(budgets),
            location_preference=pick(locations),
            possession_time=pick(possession),
            work_location=pick(["Hinjewadi", "Kharadi", "Baner", "Remote", "Hadapsar"]),
            spouse_work_location=pick(["N/A", "Kharadi", "Baner", "Magarpatta", "Viman Nagar"]),
            current_residence=pick(["Wakad", "Baner", "Pimple Saudagar", "Kothrud", "Aundh"]),
            remarks=seed_batch,
            stage=stage
        )
        db.add(ld)
        db.commit()

        # Some site visits for 'svs' + a few 'hot'
        if stage in ("svs",) or (stage == "hot" and random.random() < 0.4):
            visit_date = date.today() + timedelta(days=random.randint(-5, 10))
            sv = SiteVisit(
                lead_id=lead.id,
                project_id=pick(project_ids),
                date=visit_date.isoformat(),
                notes=pick(["Morning slot", "Client prefers evening", "Bring brochure", "Parking needed"])
            )
            db.add(sv)
            db.commit()

        leads_created.append(lead.id)

    return leads_created

# -----------------------------
# Main seeding flow
# -----------------------------

def main():
    print("⚠️  Dropping all tables…")
    Base.metadata.drop_all(bind=engine)

    print("🧱 Creating tables…")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("👤 Seeding users…")
        u = seed_users(db)

        print("🏗️ Seeding projects + info…")
        project_ids = seed_projects(db)

        print("📞 Seeding leads + details (+ some site visits)…")
        lead_ids = seed_leads(db, u["telecallers"], project_ids)

        print("\n✅ Seed complete.")
        print(f"Admins: 1 | Managers: {len(u['managers'])} | Telecallers: {len(u['telecallers'])}")
        print(f"Projects: {len(project_ids)} | Leads: {len(lead_ids)}")
        print("Use telecaller phones: 2222221111 / 2222222222 / 2222223333")
        print("Passwords: tele1 / tele2 / tele3 (manager1/manager2 for managers, admin for admin)")
    finally:
        db.close()

if __name__ == "__main__":
    main()
