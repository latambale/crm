from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from app.session import get_current_user
from app.utils.templates import templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.models import User, Lead

router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    if user.role == "agent":
        return RedirectResponse("/my-leads")

    results = (
        db.query(func.date(Lead.updated_at), func.count())
        .filter(Lead.status == "converted")
        .group_by(func.date(Lead.updated_at))
        .order_by(func.date(Lead.updated_at))
        .all()
    )
    chart_data = {
        "labels": [r[0] for r in results],
        "data": [r[1] for r in results],
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "chart_data": chart_data}
    )


@router.get("/upload-leads", response_class=HTMLResponse)
async def upload_leads_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")
    return templates.TemplateResponse("upload_leads.html", {"request": request})

@router.get("/active-leads", response_class=HTMLResponse)
def show_leads(request: Request, status: str = "all", db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")

    query = db.query(Lead)
    if status == "converted":
        query = query.filter(Lead.status == "converted")
    elif status == "unconverted":
        query = query.filter(Lead.status != "converted")
    elif status == "waiting":
        query = query.filter(Lead.status == None)

    leads = query.all()
    return templates.TemplateResponse("active_leads.html", {
        "request": request,
        "leads": leads,
        "status_filter": status,
        "user": user
    })

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
        lead.converted = True
        db.commit()

    return RedirectResponse("/my-leads", status_code=302)

@router.get("/agents", response_class=HTMLResponse)
def view_agents(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")

    agents = db.query(User).filter(User.role == "agent").all()

    agent_data = []
    for agent in agents:
        total_leads = db.query(Lead).filter(Lead.assigned_to == agent.username).count()
        converted_leads = db.query(Lead).filter(
            Lead.assigned_to == agent.username,
            Lead.converted == True
        ).count()
        conversion_rate = (
            f"{(converted_leads / total_leads) * 100:.1f}%" if total_leads else "0%"
        )

        agent_data.append({
            "id": agent.id,
            "username": agent.username,
            "email": agent.email,
            "status": agent.status,
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "conversion_rate": conversion_rate
        })

    return templates.TemplateResponse("admin_agents.html", {
        "request": request,
        "user": user,
        "agents": agent_data
    })


@router.get("/admin/agents", response_class=HTMLResponse)
def admin_agents(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")
    agents = db.query(User).filter(User.role == 'agent').all()
    return templates.TemplateResponse("admin_agents.html", {"request": request, "agents": agents})

@router.post("/admin/agents/update_status")
def update_agent_status(request: Request, agent_id: int = Form(...), status: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")
    agent = db.query(User).filter(User.id == agent_id).first()
    if agent:
        agent.status = status
        db.commit()
    return RedirectResponse("/admin/agents", status_code=303)

@router.get("/admin/agents/delete/{agent_id}")
def delete_agent(request: Request, agent_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")
    agent = db.query(User).filter(User.id == agent_id, User.status == "Deactivated").first()
    if agent:
        db.delete(agent)
        db.commit()
    return RedirectResponse("/admin/agents", status_code=303)

@router.get("/admin/agents/new", response_class=HTMLResponse)
def new_agent_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")
    return templates.TemplateResponse("new_agent.html", {"request": request})

@router.post("/admin/agents/new")
def create_agent(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")
    new_agent = User(username=username, password=password, email=email, role='agent', status="Active")
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return RedirectResponse("/admin/agents", status_code=303)

@router.get("/admin/agents/edit/{agent_id}", response_class=HTMLResponse)
def edit_agent_form(agent_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")
    agent = db.query(User).filter(User.id == agent_id).first()
    return templates.TemplateResponse("edit_agent.html", {"request": request, "agent": agent})

@router.post("/admin/agents/edit/{agent_id}")
def update_agent(request: Request, agent_id: int, username: str = Form(...), password: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role == "agent":
        return RedirectResponse("/my-leads")
    agent = db.query(User).filter(User.id == agent_id).first()
    if agent:
        agent.username = username
        agent.email = email
        agent.password = password
        db.commit()
    return RedirectResponse("/admin/agents", status_code=303)
