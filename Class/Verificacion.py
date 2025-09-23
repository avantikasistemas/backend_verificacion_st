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
            
            # Guardamos la información en la base de datos.
            self.querys.guardar_verificacion(data)

            # Retornamos la información.
            return self.tools.output(200, "Datos guardados con éxito.")

        except CustomException as e:
            print(f"Error al actualizar masivo: {e}")
            raise CustomException(f"{e}")

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
