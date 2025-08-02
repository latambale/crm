import io
import os
import uuid
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_302_FOUND
from app.session import get_current_user
from app.utils.templates import templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.db import get_db
from app.models import User, Lead
import pandas as pd
from typing import Optional

router = APIRouter()

UPLOAD_DIR = "uploads"

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
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    return templates.TemplateResponse("upload_leads.html", {"request": request})

@router.post("/upload-leads")
async def upload_leads(request: Request, file: UploadFile = File(...), distribute_equally: str = Form(None), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    contents = await file.read()

    # Save uploaded file temporarily if not distributing equally
    if distribute_equally != "yes":
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        return RedirectResponse(url=f"/campaign?filename={unique_filename}", status_code=302)

    # Continue with equal distribution
    df = pd.read_excel(io.BytesIO(contents))

    agents = db.query(User).filter(User.role == "agent").all()
    agent_ids = [a.id for a in agents]
    if not agent_ids:
        raise HTTPException(status_code=400, detail="No agents available to assign leads.")

    for i, (_, row) in enumerate(df.iterrows()):
        name = str(row.get("Name", "")).strip()
        phone = str(row.get("Phone", "")).strip()
        if name and phone:
            assigned_to = agent_ids[i % len(agent_ids)]
            db.add(Lead(name=name, phone=phone, assigned_to=assigned_to))

    db.commit()
    return RedirectResponse(url="/active-leads", status_code=302)

@router.get("/active-leads", response_class=HTMLResponse)
def show_leads(request: Request, status: str = "all", db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
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
    leads = db.query(Lead).filter(Lead.assigned_to == user.id).all()
    return templates.TemplateResponse("agent_leads.html", {"request": request, "leads": leads, "user": user})

@router.post("/convert-lead/{lead_id}")
async def convert_lead(lead_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "agent":
        return RedirectResponse("/login")

    form = await request.form()
    property_type = form.get("property_type")

    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.assigned_to == user.id).first()
    if lead:
        lead.status = "converted"
        lead.property_type = property_type
        lead.converted = True
        db.commit()

    return RedirectResponse("/my-leads", status_code=302)

@router.get("/agents", response_class=HTMLResponse)
def view_agents(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")

    agents = db.query(User).filter(User.role == "agent").all()

    agent_data = []
    for agent in agents:
        total_leads = db.query(Lead).filter(Lead.assigned_to == agent.id).count()
        converted_leads = db.query(Lead).filter(
            Lead.assigned_to == agent.id,
            Lead.converted == True,
            Lead.property_type != "cold"
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
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    agents = db.query(User).filter(User.role == 'agent').all()
    return templates.TemplateResponse("admin_agents.html", {"request": request, "agents": agents})

@router.post("/admin/agents/update_status")
def update_agent_status(request: Request, agent_id: int = Form(...), status: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")

    normalized_status = status.strip().lower()
    if "hold" in normalized_status:
        normalized_status = "hold"
    elif "active" in normalized_status:
        normalized_status = "active"
    elif "deactivate" in normalized_status:
        normalized_status = "deactivated"

    agent = db.query(User).filter(User.id == agent_id).first()
    if agent:
        agent.status = normalized_status
        db.commit()
    return RedirectResponse("/admin/agents", status_code=303)

@router.get("/admin/agents/delete/{agent_id}")
def delete_agent(request: Request, agent_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    agent = db.query(User).filter(User.id == agent_id, User.status == "deactivated").first()
    if agent:
        db.delete(agent)
        db.commit()
    return RedirectResponse("/admin/agents", status_code=303)

@router.get("/admin/agents/new", response_class=HTMLResponse)
def new_agent_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    return templates.TemplateResponse("new_agent.html", {"request": request})

@router.post("/admin/agents/new")
def create_agent(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    new_agent = User(username=username, password=password, email=email, role='agent', status="active")
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return RedirectResponse("/admin/agents", status_code=303)

@router.get("/admin/agents/edit/{agent_id}", response_class=HTMLResponse)
def edit_agent_form(agent_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    agent = db.query(User).filter(User.id == agent_id).first()
    return templates.TemplateResponse("edit_agent.html", {"request": request, "agent": agent})

@router.post("/admin/agents/edit/{agent_id}")
def update_agent(request: Request, agent_id: int, username: str = Form(...), password: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    agent = db.query(User).filter(User.id == agent_id).first()
    if agent:
        agent.username = username
        agent.email = email
        agent.password = password
        db.commit()
    return RedirectResponse("/admin/agents", status_code=303)

@router.get("/campaign", response_class=HTMLResponse)
def campaign(request: Request, filename: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")

    agents = db.query(User).filter(
        func.lower(User.role) == "agent",
        func.lower(User.status) == "active"
    ).all()

    leads = []
    if filename:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            leads = df.to_dict(orient="records")
        else:
            raise HTTPException(status_code=400, detail=f"Lead file not found: {filename}")

    return templates.TemplateResponse("campaign.html", {
        "request": request,
        "agents": agents,
        "filename": filename,
        "leads": leads
    })

@router.post("/campaign/assign")
async def assign_leads (
        request: Request,
        filename: str = Form(...),
        mode: str = Form(...),
        db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if user.role != "admin":
        return RedirectResponse("/my-leads")
    form = await request.form()
    form = dict(form)
    del form["filename"]
    del form["mode"]

    # Step 1: Parse lead data from Excel
    file_path = os.path.join(UPLOAD_DIR, filename)
    print("Checking file path:", file_path)  # Add this line
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Lead file not found.")

    df = pd.read_excel(file_path)
    df = df.dropna(subset=["Name", "Phone"])
    leads = df.to_dict(orient="records")
    total_leads = len(leads)

    # Step 2: Parse agent input (count or percentage)
    agent_distribution = {}
    for key, value in form.items():
        if key.startswith("agent_"):
            agent_id = key.split("_")[1]
            try:
                agent_distribution[agent_id] = max(0, int(value.strip()))
            except (ValueError, AttributeError):
                raise HTTPException(status_code=400, detail=f"Invalid value for agent {agent_id}")

    if not agent_distribution:
        raise HTTPException(status_code=400, detail="No agent data submitted.")

    final_counts = {}

    if mode == "count":
        final_counts = agent_distribution.copy()

    elif mode == "percentage":
        total_percent = sum(agent_distribution.values())
        if total_percent == 0:
            raise HTTPException(status_code=400, detail="Total percentage must be greater than 0.")
        for agent_id, percent in agent_distribution.items():
            count = round((percent / total_percent) * total_leads)
            final_counts[agent_id] = count

    else:
        raise HTTPException(status_code=400, detail="Invalid assignment mode selected.")

    # Step 3: Check over-assignment
    total_assigned = sum(final_counts.values())
    if total_assigned > total_leads:
        raise HTTPException(status_code=400, detail="Assigned leads exceed total leads.")
    elif total_assigned < total_leads:
        print("⚠️ Not all leads are assigned. You may want to distribute remaining leads manually.")

    # Step 4: Assign leads
    idx = 0
    for agent_id_str, count in final_counts.items():
        agent_id = int(agent_id_str)
        for _ in range(count):
            if idx >= total_leads:
                break
            lead_data = leads[idx]
            lead = Lead(
                name=lead_data.get("Name"),
                phone=lead_data.get("Phone"),
                assigned_to=agent_id,
                converted=False
            )
            db.add(lead)
            idx += 1

    db.commit()

    return RedirectResponse("/active-leads", status_code=HTTP_302_FOUND)

@router.get("/property-trends", response_class=HTMLResponse)
def property_trends(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        return RedirectResponse("/login")

    # Fetch property type trends for converted leads
    property_type_stats = (
        db.query(Lead.property_type, func.count())
        .filter(Lead.converted == True, Lead.property_type != "cold")
        .group_by(Lead.property_type)
        .order_by(func.count().desc())
        .all()
    )

    property_type_data = {
        "labels": [pt[0] for pt in property_type_stats],
        "data": [pt[1] for pt in property_type_stats],
    }

    return templates.TemplateResponse("property_trends.html", {
        "request": request,
        "user": user,
        "property_type_data": property_type_data
    })
