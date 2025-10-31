from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Inspeccion import Inspeccion
from Utils.decorator import http_decorator
from Config.db import get_db

inspeccion_router = APIRouter()

@inspeccion_router.post('/obtener_tipo_inspeccion', tags=["Inspeccion"], response_model=dict)
@http_decorator
def obtener_tipo_inspeccion(request: Request, db: Session = Depends(get_db)):
    response = Inspeccion(db).obtener_tipo_inspeccion()
    return response

@inspeccion_router.post('/obtener_aspectos_por_tipo_inspeccion', tags=["Inspeccion"], response_model=dict)
@http_decorator
def obtener_aspectos_por_tipo_inspeccion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Inspeccion(db).obtener_aspectos_por_tipo_inspeccion(data)
    return response
