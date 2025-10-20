from sqlalchemy import Column, Integer, DateTime
from Config.db import BASE
from datetime import datetime

class IntranetResponsableXLugarModel(BASE):
    __tablename__ = 'intranet_responsable_x_lugar'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lugar_id = Column(Integer, nullable=False)
    responsable_id = Column(Integer, nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
