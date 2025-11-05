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
            # Si flag_excel es True, exportar a Excel
            if data.get("flag_excel", False):
                resultado = self.querys.cargar_datos_carga(data)
                excel_data = self.exportar_excel_carga(resultado["registros"], data.get("tipo_inspeccion_id"))
                return Response(
                    content=excel_data["output"].read(),
                    headers=excel_data["headers"],
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            resultado = self.querys.cargar_datos_carga(data)
            
            return self.tools.output(200, "Datos cargados correctamente.", resultado)

        except CustomException as e:
            print(f"Error al cargar datos de inspección: {e}")
            raise CustomException(f"{e}")

    # Función para exportar datos de inspecciones de carga a Excel
    def exportar_excel_carga(self, registros: list, tipo_inspeccion_id: int):
        """
        Exporta los registros de inspecciones de carga a un archivo Excel
        con formato similar a la imagen proporcionada.
        
        Args:
            registros: Lista de inspecciones con sus aspectos
            tipo_inspeccion_id: ID del tipo de inspección para filtrar
        """
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            from openpyxl.utils import get_column_letter
            
            # Crear un nuevo workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Inspecciones"
            
            # Definir estilos
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=11)
            subheader_fill = PatternFill(start_color="B4C7E7", end_color="B4C7E7", fill_type="solid")
            subheader_font = Font(bold=True, size=10)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            # Obtener el tipo de inspección para el título
            tipo_nombre = registros[0]["tipo_inspeccion_nombre"] if registros else "Inspección"
            
            # Título principal
            ws.merge_cells('A1:Z1')
            ws['A1'] = f"LISTA DE CHEQUEO - {tipo_nombre.upper()}"
            ws['A1'].font = Font(bold=True, size=14)
            ws['A1'].alignment = center_alignment
            ws['A1'].fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            
            # Si no hay registros, retornar archivo vacío
            if not registros:
                output = BytesIO()
                wb.save(output)
                output.seek(0)
                headers = {
                    "Content-Disposition": f"attachment; filename=inspeccion_{tipo_nombre.replace(' ', '_')}.xlsx",
                    "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                }
                return {"output": output, "headers": headers}
            
            # Obtener todos los aspectos únicos y sus secciones del primer registro
            aspectos_header = []
            for seccion in registros[0].get("aspectos", []):
                for aspecto in seccion["aspectos"]:
                    aspectos_header.append({
                        "seccion": seccion["seccion_nombre"],
                        "aspecto": aspecto["aspecto_nombre"]
                    })
            
            # Fila 3: Encabezados de columnas principales
            current_row = 3
            col_index = 1
            
            # Columnas fijas iniciales
            columnas_fijas = []
            
            # Agregar columnas según el tipo de inspección (con FECHA primero)
            if tipo_inspeccion_id == 1:  # Carga Suelta
                columnas_fijas = [
                    "FECHA",
                    "REGISTRO",
                    "ADUANA",
                    "RESPONSABLE",
                    "USUARIO",
                    "NUMERO CONTENEDOR",
                    "N° SELLO SEGURIDAD",
                    "DOCUMENTO TRANSPORTE"
                ]
            elif tipo_inspeccion_id == 2:  # Contenedores
                columnas_fijas = [
                    "FECHA",
                    "REGISTRO",
                    "ADUANA",
                    "RESPONSABLE",
                    "USUARIO",
                    "EMPRESA TRANSPORTE",
                    "NUMERO CONTENEDOR",
                    "PLACA VEHICULO"
                ]
            else:
                columnas_fijas = [
                    "FECHA",
                    "REGISTRO",
                    "ADUANA",
                    "RESPONSABLE",
                    "USUARIO"
                ]
            
            # Escribir columnas fijas
            for col_name in columnas_fijas:
                cell = ws.cell(row=current_row, column=col_index)
                cell.value = col_name
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
                cell.border = border
                col_index += 1
            
            # Agrupar aspectos por sección para los encabezados
            secciones_agrupadas = {}
            for item in aspectos_header:
                seccion = item["seccion"]
                if seccion not in secciones_agrupadas:
                    secciones_agrupadas[seccion] = []
                secciones_agrupadas[seccion].append(item["aspecto"])
            
            # Fila 2: Encabezados de sección (merge cells)
            current_col = len(columnas_fijas) + 1
            for seccion, aspectos in secciones_agrupadas.items():
                start_col = current_col
                end_col = current_col + len(aspectos) - 1
                
                # Merge cells para el nombre de la sección
                if start_col == end_col:
                    cell = ws.cell(row=2, column=start_col)
                else:
                    ws.merge_cells(start_row=2, start_column=start_col, end_row=2, end_column=end_col)
                    cell = ws.cell(row=2, column=start_col)
                
                cell.value = seccion.upper()
                cell.font = subheader_font
                cell.fill = subheader_fill
                cell.alignment = center_alignment
                cell.border = border
                
                current_col += len(aspectos)
            
            # Fila 3: Nombres de aspectos individuales con numeración jerárquica
            seccion_counter = {}
            for item in aspectos_header:
                cell = ws.cell(row=current_row, column=col_index)
                
                # Obtener el índice de la sección
                seccion = item["seccion"]
                if seccion not in seccion_counter:
                    seccion_counter[seccion] = {
                        "numero_seccion": len(seccion_counter) + 1,
                        "contador_aspecto": 0
                    }
                
                seccion_counter[seccion]["contador_aspecto"] += 1
                
                # Crear numeración jerárquica (ej: 1.1, 1.2, 2.1, 2.2, etc.)
                numero_seccion = seccion_counter[seccion]["numero_seccion"]
                numero_aspecto = seccion_counter[seccion]["contador_aspecto"]
                cell.value = f"{numero_seccion}.{numero_aspecto}"
                
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
                cell.border = border
                col_index += 1
            
            # Columnas finales (FECHA ya está en columnas_fijas)
            columnas_finales = ["NOVEDADES"]
            for col_name in columnas_finales:
                cell = ws.cell(row=current_row, column=col_index)
                cell.value = col_name
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
                cell.border = border
                col_index += 1
            
            # Escribir datos de cada registro
            current_row = 4
            for registro in registros:
                col_index = 1
                
                # Escribir columnas fijas (con FECHA primero)
                if tipo_inspeccion_id == 1:  # Carga Suelta
                    valores_fijos = [
                        registro.get("fecha_creacion", ""),
                        registro["id"],
                        registro.get("aduana_nombre", "N/A"),
                        registro.get("responsable_aduana_nombre", "N/A"),
                        registro.get("usuario", "N/A"),
                        registro.get("numero_contenedor", "N/A"),
                        registro.get("numero_sello_seguridad", "N/A"),
                        registro.get("documento_transporte", "N/A")
                    ]
                elif tipo_inspeccion_id == 2:  # Contenedores
                    valores_fijos = [
                        registro.get("fecha_creacion", ""),
                        registro["id"],
                        registro.get("aduana_nombre", "N/A"),
                        registro.get("responsable_aduana_nombre", "N/A"),
                        registro.get("usuario", "N/A"),
                        registro.get("empresa_transporte", "N/A"),
                        registro.get("numero_contenedor", "N/A"),
                        registro.get("placa_vehiculo", "N/A")
                    ]
                else:
                    valores_fijos = [
                        registro.get("fecha_creacion", ""),
                        registro["id"],
                        registro.get("aduana_nombre", "N/A"),
                        registro.get("responsable_aduana_nombre", "N/A"),
                        registro.get("usuario", "N/A")
                    ]
                
                for valor in valores_fijos:
                    cell = ws.cell(row=current_row, column=col_index)
                    cell.value = valor if valor else "N/A"
                    cell.alignment = center_alignment
                    cell.border = border
                    col_index += 1
                
                # Crear diccionario de aspectos del registro actual para búsqueda rápida
                aspectos_dict = {}
                for seccion in registro.get("aspectos", []):
                    for aspecto in seccion["aspectos"]:
                        aspectos_dict[aspecto["aspecto_nombre"]] = aspecto["valor"]
                
                # Escribir valores de aspectos en el orden correcto
                for item in aspectos_header:
                    cell = ws.cell(row=current_row, column=col_index)
                    valor = aspectos_dict.get(item["aspecto"], "N/A")
                    cell.value = valor
                    cell.alignment = center_alignment
                    cell.border = border
                    
                    # Aplicar color según el valor
                    if valor == "SI":
                        cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                    elif valor == "NO":
                        cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                    
                    col_index += 1
                
                # Escribir novedades (FECHA ya no va al final)
                cell = ws.cell(row=current_row, column=col_index)
                cell.value = registro.get("novedades", "")
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
                cell.border = border
                
                current_row += 1
            
            # Ajustar ancho de columnas
            for col in range(1, col_index + 1):
                column_letter = get_column_letter(col)
                if col <= len(columnas_fijas):
                    ws.column_dimensions[column_letter].width = 20
                elif col > col_index - 2:
                    ws.column_dimensions[column_letter].width = 25
                else:
                    ws.column_dimensions[column_letter].width = 8
            
            # Ajustar altura de filas
            ws.row_dimensions[1].height = 25
            ws.row_dimensions[2].height = 20
            ws.row_dimensions[3].height = 30
            
            # Guardar en BytesIO
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            
            headers = {
                "Content-Disposition": f"attachment; filename=inspeccion_{tipo_nombre.replace(' ', '_')}.xlsx",
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
            
            return {"output": output, "headers": headers}
            
        except Exception as e:
            print(f"Error al exportar Excel: {str(e)}")
            raise CustomException(f"Error al exportar Excel: {str(e)}")

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

