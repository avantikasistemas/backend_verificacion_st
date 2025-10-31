from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class IntranetInspeccionCargaDetalleModel(BASE):
    __tablename__ = "intranet_inspeccion_carga_detalle"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspeccion_carga_id = Column(Integer, nullable=False)
    aspecto_id = Column(Integer, nullable=False)
    valor_seleccionado = Column(Integer, nullable=False)  # 0=NO, 1=SI, 2=N/A
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())

    def __init__(self, data):
        self.inspeccion_carga_id = data.get("inspeccion_carga_id")
        self.aspecto_id = data.get("aspecto_id")
        self.valor_seleccionado = data.get("valor_seleccionado")
        self.estado = data.get("estado", 1)
