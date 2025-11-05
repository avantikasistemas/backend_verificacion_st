from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Login import Login
from Utils.decorator import http_decorator
from Config.db import get_db
from fastapi.responses import Response as FastAPIResponse

login_router = APIRouter()

@login_router.post('/login', tags=["Login"], response_model=dict)
@http_decorator
def login(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Login(db).login(data)
    return response
