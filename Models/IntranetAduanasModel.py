from sqlalchemy import Column, Integer, DateTime, String
from Config.db import BASE
from datetime import datetime

class IntranetAduanasModel(BASE):
    __tablename__ = 'intranet_aduanas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
