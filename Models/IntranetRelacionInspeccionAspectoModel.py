from sqlalchemy import Column, Integer, DateTime
from Config.db import BASE
from Utils.datetime_utils import get_colombia_time

class IntranetRelacionInspeccionAspectoModel(BASE):
    __tablename__ = 'intranet_relacion_inspeccion_aspecto'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_inspeccion_id = Column(Integer, nullable=False)
    tipo_aspecto_id = Column(Integer, nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=get_colombia_time)
