from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from fastapi import Response
import pandas as pd
from io import BytesIO

class Verificacion:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función guardar masivo
    def guardar_verificacion(self, data: dict):
        """ Api que realiza el guardado de los datos. """
        try:
            # Validar que los campos principales existan
            if not data.get("lugar_inspeccion_id"):
                raise CustomException("El campo lugar_inspeccion_id es requerido.")

            if not data.get("responsable_verificacion_id"):
                raise CustomException("El campo responsable_verificacion_id es requerido.")

            if not data.get("novedades"):
                raise CustomException("El campo novedades es requerido.")

            # Validar aspectos generales
            aspectos_generales = data.get("aspectos_generales", {})
            self._validar_aspectos(aspectos_generales, "aspectos_generales", 4)
            
            # Validar paredes
            paredes = data.get("paredes", {})
            self._validar_aspectos(paredes, "paredes", 4)
            
            # Validar puertas
            puertas = data.get("puertas", {})
            self._validar_aspectos(puertas, "puertas", 5)
            
            # Validar piso
            piso = data.get("piso", {})
            self._validar_aspectos(piso, "piso", 4)
            
            # Validar techo
            techo = data.get("techo", {})
            self._validar_aspectos(techo, "techo", 3)
            
            # Validar seguridad
            seguridad = data.get("seguridad", {})
            self._validar_aspectos(seguridad, "seguridad", 4)
            
            # Guardamos la información en la base de datos.
            self.querys.guardar_verificacion(data)

            # Retornamos la información.
            return self.tools.output(200, "Datos guardados con éxito.", data)

        except CustomException as e:
            print(f"Error al guardar verificación: {e}")
            raise CustomException(f"{e}")
    
    # Función auxiliar para validar aspectos
    def _validar_aspectos(self, aspectos: dict, nombre_seccion: str, cantidad_esperada: int):
        """
        Valida que todos los aspectos de una sección tengan valores válidos (0, 1, o 2).
        
        Args:
            aspectos: Diccionario con los aspectos a validar
            nombre_seccion: Nombre de la sección para mensajes de error
            cantidad_esperada: Cantidad de aspectos que debe tener la sección
        """
        if not aspectos:
            raise CustomException(f"La sección '{nombre_seccion}' es requerida.")
        
        # Verificar que tenga la cantidad correcta de aspectos
        if len(aspectos) != cantidad_esperada:
            raise CustomException(
                f"La sección '{nombre_seccion}' debe tener {cantidad_esperada} aspectos, pero tiene {len(aspectos)}."
            )
        
        # Validar cada aspecto
        for key, value in aspectos.items():
            # Verificar que no sea None o vacío
            if value is None or value == "":
                raise CustomException(
                    f"El campo '{key}' en la sección '{nombre_seccion}' no puede estar vacío o nulo. "
                    f"Debe tener un valor: 0 (NO), 1 (SI) o 2 (N/A)."
                )
            
            # Convertir a string para validación uniforme
            value_str = str(value)
            
            # Verificar que sea uno de los valores permitidos
            if value_str not in ["0", "1", "2"]:
                raise CustomException(
                    f"El campo '{key}' en la sección '{nombre_seccion}' tiene un valor inválido '{value}'. "
                    f"Solo se permiten los valores: 0 (NO), 1 (SI) o 2 (N/A)."
                )

    # Función para cargar los datos registrados
    def cargar_datos(self, data: dict):
        """ Api que realiza la carga de los datos. """
        try:
            
            if data["flag_excel"]:
                registros = self.querys.cargar_datos(data)
                datos_excel = self.exportar_excel(registros)
                return Response(
                    content=datos_excel["output"].read(), 
                    headers=datos_excel["headers"], 
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            if data["position"] <= 0:
                message = "El campo posición no es válido"
                raise CustomException(message)
            
            # Cargamos la información en la base de datos.
            datos = self.querys.cargar_datos(data)
            
            registros = datos["registros"]
            cant_registros = datos["cant_registros"]
            
            if not registros:
                message = "No hay listado de reportes que mostrar."
                return self.tools.output(200, message, data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 1,
                "registros": []
            })
                
            if cant_registros%data["limit"] == 0:
                total_pag = cant_registros//data["limit"]
            else:
                total_pag = cant_registros//data["limit"] + 1
                
            if total_pag < int(data["position"]):
                message = "La posición excede el número total de registros."
                return self.tools.output(200, message, data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })

            registros_dict = {
                "total_registros": cant_registros,
                "total_pag": total_pag,
                "posicion_pag": data["position"],
                "registros": registros
            }

            # Retornamos la información.
            return self.tools.output(200, "Datos cargados con éxito.", registros_dict)

        except CustomException as e:
            print(f"Error al cargar datos: {e}")
            raise CustomException(f"{e}")

    # Función que realiza la operacion de exporte con libreria de excel
    def exportar_excel(self, datos: list):

        # Convertir los datos a un DataFrame de pandas
        df = pd.DataFrame(datos)

        # Crear un buffer de memoria para el archivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Datos")

        # Obtener los bytes del archivo y preparar la respuesta
        output.seek(0)
        headers = {
            "Content-Disposition": "attachment; filename=datos.xlsx",
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        return {"output": output, "headers": headers}

    # Función para obtener los lugares de inspección
    def obtener_lugares_inspeccion(self):
        """ Api que obtiene los lugares de inspección activos. """
        try:
            # Obtenemos los lugares de inspección desde la base de datos
            lugares = self.querys.obtener_lugares_inspeccion()
            
            if not lugares:
                message = "No hay lugares de inspección disponibles."
                return self.tools.output(200, message, data=[])
            
            # Retornamos la información
            return self.tools.output(200, "Lugares de inspección cargados con éxito.", lugares)

        except CustomException as e:
            print(f"Error al obtener lugares de inspección: {e}")
            raise CustomException(f"{e}")

    # Función para obtener los responsables por lugar de inspección
    def obtener_responsables_por_lugar(self, data: dict):
        """ Api que obtiene los responsables asociados a un lugar de inspección. """
        try:
            lugar_id = data.get("lugar_id")
            
            if not lugar_id:
                message = "El campo lugar_id es requerido."
                raise CustomException(message)
            
            # Obtenemos los responsables desde la base de datos
            responsables = self.querys.obtener_responsables_por_lugar(lugar_id)
            
            if not responsables:
                message = "No hay responsables asociados a este lugar de inspección."
                return self.tools.output(200, message, data=[])
            
            # Retornamos la información
            return self.tools.output(200, "Responsables cargados con éxito.", responsables)

        except CustomException as e:
            print(f"Error al obtener responsables: {e}")
            raise CustomException(f"{e}")
