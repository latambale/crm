from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from app.models import User
#from app.session import get_user_session
from app.db import get_db
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = next(get_db())  # ✅ Fix here
    user = db.query(User).filter_by(username=username, password=password).first()
    if user:
        request.session["user"] = user.username
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
