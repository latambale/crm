from fastapi import UploadFile, File, Depends, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db import get_db
import pandas as pd
import io
from app.models import User, Lead

router = APIRouter()

@router.post("/upload-leads")
async def upload_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))

    agents = db.query(User).filter(User.role == "agent").all()
    agent_usernames = [a.username for a in agents]

    if not agent_usernames:
        raise HTTPException(status_code=400, detail="No agents available to assign leads.")

    for i, (_, row) in enumerate(df.iterrows()):
        name = str(row.get("Name", "")).strip()
        phone = str(row.get("Phone", "")).strip()
        if name and phone:
            assigned_to = agent_usernames[i % len(agent_usernames)]
            db.add(Lead(name=name, phone=phone, assigned_to=assigned_to))

    db.commit()
    return RedirectResponse(url="/active-leads", status_code=302)