from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class IntranetInspeccionCargaImagenModel(BASE):
    __tablename__ = "intranet_inspeccion_carga_imagen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspeccion_carga_id = Column(Integer, nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())

    def __init__(self, data):
        self.inspeccion_carga_id = data.get("inspeccion_carga_id")
        self.nombre_archivo = data.get("nombre_archivo")
        self.ruta_archivo = data.get("ruta_archivo")
        self.estado = data.get("estado", 1)
