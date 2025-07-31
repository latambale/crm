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
def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@router.get("/upload-leads", response_class=HTMLResponse)
async def upload_leads_form(request: Request):
    return templates.TemplateResponse("upload_leads.html", {"request": request})

@router.get("/active-leads", response_class=HTMLResponse)
def show_leads(request: Request, db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return templates.TemplateResponse("active_leads.html", {"request": request, "leads": leads})
