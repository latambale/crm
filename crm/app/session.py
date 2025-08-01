from sqlalchemy.orm import Session
from app.models import User
from fastapi import Request


def get_current_user(request: Request, db: Session):
    username = request.session.get("user")
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()