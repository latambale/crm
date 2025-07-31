from fastapi import UploadFile, File, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Lead
import pandas as pd
import io
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.utils.templates import templates

router = APIRouter()

@router.post("/upload-leads")
async def upload_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))

    for _, row in df.iterrows():
        name = str(row.get("Name", "")).strip()
        phone = str(row.get("Phone", "")).strip()
        if name and phone:
            db.add(Lead(name=name, phone=phone))

    db.commit()
    return RedirectResponse(url="/active-leads", status_code=302)
