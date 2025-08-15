from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Date, UniqueConstraint
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True)
    password = Column(String)
    role = Column(String)

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    status = Column(String)  # 'fresh', 'in_progress', 'closed'
    assigned_to = Column(Integer, ForeignKey("users.id"))

class LeadDetails(Base):
    __tablename__ = "lead_details"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    looking_for = Column(String)
    budget = Column(String)
    location_preference = Column(String)
    possession_time = Column(String)
    work_location = Column(String)
    spouse_work_location = Column(String)
    current_residence = Column(String)
    remarks = Column(String)
    stage = Column(String)  # New, Interested, Follow-up, Not Interested
    created_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    property_type = Column(String)  # 1BHK, 2BHK, Plot, etc.
    budget_range = Column(String)  # Matchable with lead budget
    description = Column(String)

class ProjectInfo(Base):
    __tablename__ = "project_info"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)

    developer_name = Column(String)
    experience = Column(String)              # years or text
    completed_projects = Column(String)      # text/number
    landmark = Column(String)

    possession_type = Column(String)         # NewLaunch | Nearing Possession Ready | Under Construction
    total_land = Column(String)              # e.g., "5 acres"
    total_towers = Column(String)            # e.g., "6"
    number_of_floors = Column(String)        # e.g., "30"
    construction_technology = Column(String) # Mivan | Hybrid | RCC
    number_of_amenities = Column(String)     # e.g., "30"

    types_of_inventory = Column(String)      # comma-separated values
    carpet_area_json = Column(Text)          # JSON string: {"1BHK":"450-600", "2BHK":"650-800", ...}

    flats_per_floor = Column(String)         # e.g., "4/5/6"
    lifts = Column(String)                   # e.g., "3/4/5"


class SiteVisit(Base):
    __tablename__ = "site_visits"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    date = Column(String)
    notes = Column(String)


class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    telecaller_id = Column(Integer, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    in_time = Column(DateTime, nullable=True)   # store as naive UTC
    out_time = Column(DateTime, nullable=True)  # (unused now, reserved for future)
    total_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("telecaller_id", "date", name="uq_attendance_day"),
    )

class LiveLocation(Base):
    __tablename__ = "live_location"
    id = Column(Integer, primary_key=True, index=True)
    telecaller_id = Column(Integer, index=True, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class Callback(Base):
    __tablename__ = "callback"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True, nullable=False)
    telecaller_id = Column(Integer, index=True, nullable=False)
    due_at = Column(DateTime, nullable=False)   # store as NAIVE UTC
    note = Column(String, default="")
    status = Column(String, default="pending")  # pending | done | canceled
    created_at = Column(DateTime, default=datetime.utcnow)