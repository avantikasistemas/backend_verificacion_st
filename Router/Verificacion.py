from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Verificacion import Verificacion
from Utils.decorator import http_decorator
from Config.db import get_db
from fastapi.responses import Response as FastAPIResponse

verificacion_router = APIRouter()

@verificacion_router.post('/guardar_verificacion', tags=["Verificacion"], response_model=dict)
@http_decorator
def guardar_verificacion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Verificacion(db).guardar_verificacion(data)
    return response

@verificacion_router.post('/cargar_datos', tags=["Verificacion"])
@http_decorator
def cargar_datos(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Verificacion(db).cargar_datos(data)
    # Si es una respuesta de tipo FastAPI Response (Excel), devolverla directamente
    if isinstance(response, FastAPIResponse):
        return response
    return response

@verificacion_router.post('/obtener_lugares_inspeccion', tags=["Verificacion"], response_model=dict)
@http_decorator
def obtener_lugares_inspeccion(request: Request, db: Session = Depends(get_db)):
    response = Verificacion(db).obtener_lugares_inspeccion()
    return response

@verificacion_router.post('/obtener_responsables_por_lugar', tags=["Verificacion"], response_model=dict)
@http_decorator
def obtener_responsables_por_lugar(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Verificacion(db).obtener_responsables_por_lugar(data)
    return response

@verificacion_router.post('/obtener_aspectos_por_lugar', tags=["Verificacion"], response_model=dict)
@http_decorator
def obtener_aspectos_por_lugar(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Verificacion(db).obtener_aspectos_por_lugar(data)
    return response
