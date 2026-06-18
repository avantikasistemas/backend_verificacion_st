from sqlalchemy import Column, Integer, DateTime
from Config.db import BASE
from Utils.datetime_utils import get_colombia_time

class IntranetAduanaXModalidadModel(BASE):
    __tablename__ = 'intranet_aduana_x_modalidad'
    __table_args__ = {'schema': 'dbo'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    modalidad_id = Column(Integer, nullable=False)
    aduana_id = Column(Integer, nullable=False)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=get_colombia_time)
