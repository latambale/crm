from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from app.session import get_current_user
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.utils.templates import templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Lead

router = APIRouter()
#templates = Jinja2Templates(directory="app/templates")  # Adjust the path as needed

router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    if user.role == "agent":
        return RedirectResponse("/my-leads")

    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


@router.get("/upload-leads", response_class=HTMLResponse)
async def upload_leads_form(request: Request):
    return templates.TemplateResponse("upload_leads.html", {"request": request})

@router.get("/active-leads", response_class=HTMLResponse)
def show_leads(request: Request, db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return templates.TemplateResponse("active_leads.html", {"request": request, "leads": leads})

@router.get("/my-leads", response_class=HTMLResponse)
def agent_leads(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "agent":
        return RedirectResponse("/login")
    leads = db.query(Lead).filter(Lead.assigned_to == user.username).all()
    return templates.TemplateResponse("agent_leads.html", {"request": request, "leads": leads, "user": user})

@router.post("/convert-lead/{lead_id}")
async def convert_lead(lead_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "agent":
        return RedirectResponse("/login")

    form = await request.form()
    property_type = form.get("property_type")

    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.assigned_to == user.username).first()
    if lead:
        lead.status = "converted"
        lead.property_type = property_type
        db.commit()

    return RedirectResponse("/my-leads", status_code=302)
