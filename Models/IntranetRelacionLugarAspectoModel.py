from sqlalchemy import Column, Integer, DateTime
from Config.db import BASE
from Utils.datetime_utils import get_colombia_time

class IntranetRelacionLugarAspectoModel(BASE):
    __tablename__ = 'intranet_relacion_lugar_aspecto'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lugar_inspeccion_id = Column(Integer, nullable=False)
    aspecto_infraestructura_id = Column(Integer, nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=get_colombia_time)
