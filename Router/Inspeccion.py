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

@inspeccion_router.post('/guardar_carga', tags=["Inspeccion"], response_model=dict)
@http_decorator
def guardar_carga(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Inspeccion(db).guardar_carga(data)
    return response

@inspeccion_router.post('/cargar_datos_carga', tags=["Inspeccion"], response_model=dict)
@http_decorator
def cargar_datos_carga(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Inspeccion(db).cargar_datos_carga(data)
    return response

@inspeccion_router.post('/obtener_aduanas', tags=["Inspeccion"], response_model=dict)
@http_decorator
def obtener_aduanas(request: Request, db: Session = Depends(get_db)):
    response = Inspeccion(db).obtener_aduanas()
    return response

@inspeccion_router.post('/obtener_responsables_por_aduana', tags=["Inspeccion"], response_model=dict)
@http_decorator
def obtener_responsables_por_aduana(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Inspeccion(db).obtener_responsables_por_aduana(data)
    return response
