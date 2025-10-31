from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from fastapi import Response
import pandas as pd
from io import BytesIO

class Inspeccion:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función para cargar los datos registrados
    def obtener_tipo_inspeccion(self):
        """ Api que retorna los tipos de inspección activos. """
        try:
            data = self.querys.obtener_tipo_inspeccion()

            return self.tools.output(200, "Datos encontrados.", data)

        except CustomException as e:
            print(f"Error al obtener tipos de inspección: {e}")
            raise CustomException(f"{e}")

    # Función para obtener aspectos según tipo de inspección
    def obtener_aspectos_por_tipo_inspeccion(self, data: dict):
        """ Api que retorna los aspectos de carga según el tipo de inspección. """
        try:
            tipo_inspeccion_id = data.get("tipo_inspeccion_id")
            data = self.querys.obtener_aspectos_por_tipo_inspeccion(tipo_inspeccion_id)
            
            return self.tools.output(200, "Aspectos obtenidos correctamente.", data)

        except CustomException as e:
            print(f"Error al obtener aspectos: {e}")
            raise CustomException(f"{e}")
