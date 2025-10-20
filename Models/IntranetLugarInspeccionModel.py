from sqlalchemy import Column, Integer, String, DateTime
from Config.db import BASE
from datetime import datetime

class IntranetLugarInspeccionModel(BASE):
    __tablename__ = 'intranet_lugar_inspeccion'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
