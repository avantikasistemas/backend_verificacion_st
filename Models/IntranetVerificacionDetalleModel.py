from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class IntranetVerificacionDetalleModel(BASE):
    __tablename__ = "intranet_verificacion_detalle"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verificacion_id = Column(Integer, nullable=False)
    aspecto_id = Column(Integer, nullable=False)
    valor_seleccionado = Column(Integer, nullable=False)  # 0=NO, 1=SI, 2=N/A
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())

    def __init__(self, data):
        self.verificacion_id = data.get("verificacion_id")
        self.aspecto_id = data.get("aspecto_id")
        self.valor_seleccionado = data.get("valor_seleccionado")
        self.estado = data.get("estado", 1)
