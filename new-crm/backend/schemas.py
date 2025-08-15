# backend/schemas.py
from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    phone: str
    password: str

class ManagerCreate(BaseModel):
    phone: str
    password: str

class ManagerUpdate(BaseModel):
    phone: str
    password: str

class LeadFormData(BaseModel):
    lead_id: int
    looking_for: str
    budget: str
    location_preference: str
    possession_time: str
    work_location: str
    spouse_work_location: str
    current_residence: str
    remarks: str
    stage: str

class SVSData(BaseModel):
    lead_id: int
    project_id: int
    date: str  # "YYYY-MM-DD"
    notes: str = ""

class CallOutcome(BaseModel):
    lead_id: int
    connected: bool
    reason: Optional[str] = ""

class AttendanceIn(BaseModel):
    telecaller_id: int
    timestamp: Optional[str] = None  # ISO string from client

class LiveLocationIn(BaseModel):
    telecaller_id: int
    lat: float
    lng: float
    accuracy: Optional[float] = None
    timestamp: Optional[str] = None  # ISO optional

class CallbackIn(BaseModel):
    lead_id: int
    telecaller_id: int
    due_at: str                    # ISO string from client (local or UTC)
    note: str = ""

class CallbackUpdate(BaseModel):
    due_at: str | None = None      # ISO
    note: str | None = None
    status: str | None = None      # pending | done | canceled

class SVSUpdate(BaseModel):
    date: Optional[str] = None     # ISO like "2025-08-15T14:00"
    notes: Optional[str] = None
    project_id: Optional[int] = None

class UploadListItem(BaseModel):
    id: str
    telecaller_id: int
    url: str
    filename: str
    description: str
    kind: str
    mime: str
    size: int
    created_at: str
    lat: Optional[float] = None
    lng: Optional[float] = None