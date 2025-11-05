from sqlalchemy import Column, Integer, String, DateTime, Text
from Config.db import BASE
from datetime import datetime

class IntranetVerificacionModel(BASE):
    __tablename__ = 'intranet_verificacion_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lugar_inspeccion_id = Column(Integer, nullable=False)
    responsable_verificacion_id = Column(Integer, nullable=False)
    novedades = Column(Text, nullable=True)
    usuario = Column(String(50), nullable=True)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)

    def __init__(self, data):
        self.lugar_inspeccion_id = data.get("lugar_inspeccion_id")
        self.responsable_verificacion_id = data.get("responsable_verificacion_id")
        self.novedades = data.get("novedades")
        self.usuario = data.get("usuario")
