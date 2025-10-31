from sqlalchemy import Column, Integer, DateTime, Text
from Config.db import BASE
from datetime import datetime

class IntranetAspectosCargaModel(BASE):
    __tablename__ = 'intranet_aspectos_carga'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_inspeccion = Column(Integer, nullable=False)
    tipo_aspecto_id = Column(Integer, nullable=False)
    nombre = Column(Text, nullable=True)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
