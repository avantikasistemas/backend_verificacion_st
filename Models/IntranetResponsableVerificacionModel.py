from sqlalchemy import Column, Integer, String, DateTime
from Config.db import BASE
from Utils.datetime_utils import get_colombia_time

class IntranetResponsableVerificacionModel(BASE):
    __tablename__ = 'intranet_responsable_verificacion'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=get_colombia_time)
