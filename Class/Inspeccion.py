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

    # Función para guardar inspección de carga
    def guardar_carga(self, data: dict):
        """ Api que guarda una inspección de carga con aspectos dinámicos e imágenes. """
        try:
            resultado = self.querys.guardar_carga(data)
            
            if resultado:
                return self.tools.output(200, "Inspección guardada correctamente.", None)
            else:
                return self.tools.output(500, "Error al guardar la inspección.", None)

        except CustomException as e:
            print(f"Error al guardar inspección: {e}")
            raise CustomException(f"{e}")

    # Función para cargar datos de inspecciones guardadas
    def cargar_datos_carga(self, data: dict):
        """ Api que retorna las inspecciones guardadas con sus aspectos e imágenes. """
        try:
            resultado = self.querys.cargar_datos_carga(data)
            
            return self.tools.output(200, "Datos cargados correctamente.", resultado)

        except CustomException as e:
            print(f"Error al cargar datos de inspección: {e}")
            raise CustomException(f"{e}")

    # Función para obtener las aduanas activas
    def obtener_aduanas(self):
        """ Api que retorna las aduanas activas. """
        try:
            result = self.querys.obtener_aduanas()

            return self.tools.output(200, "Aduanas obtenidas correctamente.", result)

        except CustomException as e:
            print(f"Error al obtener aduanas: {e}")
            raise CustomException(f"{e}")

    # Función para obtener responsables por aduana
    def obtener_responsables_por_aduana(self, data: dict):
        """ Api que retorna los responsables asociados a una aduana. """
        try:
            aduana_id = data.get("aduana_id")
            data = self.querys.obtener_responsables_por_aduana(aduana_id)
            
            return self.tools.output(200, "Responsables obtenidos correctamente.", data)

        except CustomException as e:
            print(f"Error al obtener responsables por aduana: {e}")
            raise CustomException(f"{e}")

