from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class IntranetVerificacionImagenModel(BASE):
    __tablename__ = "intranet_verificacion_imagen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verificacion_id = Column(Integer, nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())

    def __init__(self, data):
        self.verificacion_id = data.get("verificacion_id")
        self.nombre_archivo = data.get("nombre_archivo")
        self.ruta_archivo = data.get("ruta_archivo")
        self.estado = data.get("estado", 1)
