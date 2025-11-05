from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class IntranetInspeccionCargaModel(BASE):
    __tablename__ = "intranet_inspeccion_carga"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_inspeccion_id = Column(Integer, nullable=False)
    novedades = Column(Text, nullable=True)
    numero_contenedor = Column(Text, nullable=True)
    numero_sello_seguridad = Column(Text, nullable=True)
    documento_transporte = Column(Text, nullable=True)
    empresa_transporte = Column(Text, nullable=True)
    placa_vehiculo = Column(Text, nullable=True)
    aduana_id = Column(Integer, nullable=True)
    responsable_aduana_id = Column(Integer, nullable=True)
    usuario = Column(String(50), nullable=True)
    estado = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())

    def __init__(self, data):
        self.tipo_inspeccion_id = data.get("tipo_inspeccion_id")
        self.novedades = data.get("novedades")
        self.numero_contenedor = data.get("numero_contenedor")
        self.numero_sello_seguridad = data.get("numero_sello_seguridad")
        self.documento_transporte = data.get("documento_transporte")
        self.empresa_transporte = data.get("empresa_transporte")
        self.placa_vehiculo = data.get("placa_vehiculo")
        self.aduana_id = data.get("aduana_id")
        self.responsable_aduana_id = data.get("responsable_aduana_id")
        self.usuario = data.get("usuario")
        self.estado = data.get("estado", 1)
