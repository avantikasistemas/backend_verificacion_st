from Utils.tools import Tools, CustomException
from Utils.image_utils import ImageUtils
from sqlalchemy import text, func
from datetime import date, datetime
from Models.IntranetVerificacionModel import IntranetVerificacionModel
from Models.IntranetLugarInspeccionModel import IntranetLugarInspeccionModel
from Models.IntranetResponsableXLugarModel import IntranetResponsableXLugarModel
from Models.IntranetResponsableVerificacionModel import IntranetResponsableVerificacionModel
from Models.IntranetTipoInspeccionModel import IntranetTipoInspeccionModel
from Models.IntranetAspectosCargaModel import IntranetAspectosCargaModel
from Models.IntranetRelacionInspeccionAspectoModel import IntranetRelacionInspeccionAspectoModel
from Models.IntranetTipoAspectosInfraestructuraModel import IntranetTipoAspectosInfraestructuraModel
from Models.IntranetAspectosInfraestructuraModel import IntranetAspectosInfraestructuraModel
from Models.IntranetInspeccionCargaModel import IntranetInspeccionCargaModel
from Models.IntranetInspeccionCargaDetalleModel import IntranetInspeccionCargaDetalleModel
from Models.IntranetInspeccionCargaImagenModel import IntranetInspeccionCargaImagenModel
from Models.IntranetAduanasModel import IntranetAduanasModel
from Models.IntranetResponsableXAduanasModel import IntranetResponsableXAduanasModel

class Querys:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.query_params = dict()

    # Función auxiliar para convertir valores numéricos a símbolos
    def _convertir_valor_aspecto(self, valor):
        """
        Convierte valores numéricos de aspectos a símbolos visuales.
        1 = ✔ (SI)
        0 = ✖ (NO)
        2 = NA (No Aplica)
        """
        if valor == 1:
            return "✔"
        elif valor == 0:
            return "✖"
        elif valor == 2:
            return "NA"
        else:
            return valor  # En caso de valor inesperado, retornar el original

    # Función auxiliar para convertir valores numéricos a texto para Excel
    def _convertir_valor_aspecto_excel(self, valor):
        """
        Convierte valores numéricos de aspectos a texto para exportación Excel.
        1 = SI
        0 = NO
        2 = NO APLICA
        """
        if valor == 1:
            return "SI"
        elif valor == 0:
            return "NO"
        elif valor == 2:
            return "NO APLICA"
        else:
            return valor  # En caso de valor inesperado, retornar el original

    # Query para guardar verificacion
    def guardar_verificacion(self, data: dict):
        try:
            # Extraer los objetos anidados
            aspectos_generales = data.get("aspectos_generales", {})
            paredes = data.get("paredes", {})
            puertas = data.get("puertas", {})
            piso = data.get("piso", {})
            techo = data.get("techo", {})
            seguridad = data.get("seguridad", {})
            
            # Crear el diccionario con la estructura que espera el modelo
            datos_modelo = {
                "lugar_inspeccion_id": data.get("lugar_inspeccion_id"),
                "responsable_verificacion_id": data.get("responsable_verificacion_id"),
                # Aspectos generales
                "aspectos_1": int(aspectos_generales.get("aspecto_1")),
                "aspectos_2": int(aspectos_generales.get("aspecto_2")),
                "aspectos_3": int(aspectos_generales.get("aspecto_3")),
                "aspectos_4": int(aspectos_generales.get("aspecto_4")),
                # Paredes
                "paredes_1": int(paredes.get("paredes_1")),
                "paredes_2": int(paredes.get("paredes_2")),
                "paredes_3": int(paredes.get("paredes_3")),
                "paredes_4": int(paredes.get("paredes_4")),
                # Puertas
                "puertas_1": int(puertas.get("puertas_1")),
                "puertas_2": int(puertas.get("puertas_2")),
                "puertas_3": int(puertas.get("puertas_3")),
                "puertas_4": int(puertas.get("puertas_4")),
                "puertas_5": int(puertas.get("puertas_5")),
                # Pisos (nota: en el modelo es "pisos_" no "piso_")
                "pisos_1": int(piso.get("piso_1")),
                "pisos_2": int(piso.get("piso_2")),
                "pisos_3": int(piso.get("piso_3")),
                "pisos_4": int(piso.get("piso_4")),
                # Techo
                "techo_1": int(techo.get("techo_1")),
                "techo_2": int(techo.get("techo_2")),
                "techo_3": int(techo.get("techo_3")),
                # Seguridad
                "seguridad_1": int(seguridad.get("seguridad_1")),
                "seguridad_2": int(seguridad.get("seguridad_2")),
                "seguridad_3": int(seguridad.get("seguridad_3")),
                "seguridad_4": int(seguridad.get("seguridad_4")),
                # Novedades
                "novedades": data.get("novedades")
            }
            
            # Crear la instancia del modelo con los datos transformados
            nuevo_registro = IntranetVerificacionModel(datos_modelo)
            
            self.db.add(nuevo_registro)
            self.db.commit()
            return True
        except Exception as ex:
            self.db.rollback()
            print(f"Error al guardar verificación: {str(ex)}")
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para cargar la información registrada
    def cargar_datos(self, data: dict):
        try:
            response = list()
            
            fecha_desde = data["fecha_desde"]
            fecha_hasta = data["fecha_hasta"]
            cant_registros = 0
            limit = data["limit"]
            position = data["position"]
            flag_excel = data["flag_excel"]
            
            # Crear query base con SQLAlchemy incluyendo JOINs
            query = self.db.query(
                IntranetVerificacionModel,
                IntranetLugarInspeccionModel.nombre.label('nombre_lugar'),
                IntranetResponsableVerificacionModel.nombre.label('nombre_responsable')
            ).join(
                IntranetLugarInspeccionModel,
                IntranetVerificacionModel.lugar_inspeccion_id == IntranetLugarInspeccionModel.id
            ).join(
                IntranetResponsableVerificacionModel,
                IntranetVerificacionModel.responsable_verificacion_id == IntranetResponsableVerificacionModel.id
            ).filter(IntranetVerificacionModel.estado == 1)
            
            # Aplicar filtro de fechas si existen
            if fecha_desde and fecha_hasta:
                # Detectar el formato de fecha y convertir apropiadamente
                if '-' in fecha_desde:
                    fecha_inicio = datetime.strptime(f"{fecha_desde} 00:00:00", "%Y-%m-%d %H:%M:%S")
                    fecha_fin = datetime.strptime(f"{fecha_hasta} 23:59:59", "%Y-%m-%d %H:%M:%S")
                else:
                    fecha_inicio = datetime.strptime(f"{fecha_desde} 00:00:00", "%Y%m%d %H:%M:%S")
                    fecha_fin = datetime.strptime(f"{fecha_hasta} 23:59:59", "%Y%m%d %H:%M:%S")
                query = query.filter(IntranetVerificacionModel.created_at.between(fecha_inicio, fecha_fin))
            
            # Ordenar por id descendente
            query = query.order_by(IntranetVerificacionModel.id.desc())
            
            if flag_excel:
                # Para Excel, devolver todos los registros
                result = query.all()
                registros = [
                    {
                        "id": row.IntranetVerificacionModel.id,
                        "lugar_inspeccion": row.nombre_lugar,
                        "responsable_verificacion": row.nombre_responsable,
                        # "lugar_inspeccion_id": row.IntranetVerificacionModel.lugar_inspeccion_id,
                        # "responsable_verificacion_id": row.IntranetVerificacionModel.responsable_verificacion_id,
                        "aspectos_1": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.aspectos_1),
                        "aspectos_2": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.aspectos_2),
                        "aspectos_3": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.aspectos_3),
                        "aspectos_4": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.aspectos_4),
                        "paredes_1": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.paredes_1),
                        "paredes_2": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.paredes_2),
                        "paredes_3": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.paredes_3),
                        "paredes_4": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.paredes_4),
                        "puertas_1": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.puertas_1),
                        "puertas_2": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.puertas_2),
                        "puertas_3": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.puertas_3),
                        "puertas_4": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.puertas_4),
                        "puertas_5": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.puertas_5),
                        "pisos_1": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.pisos_1),
                        "pisos_2": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.pisos_2),
                        "pisos_3": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.pisos_3),
                        "pisos_4": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.pisos_4),
                        "techo_1": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.techo_1),
                        "techo_2": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.techo_2),
                        "techo_3": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.techo_3),
                        "seguridad_1": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.seguridad_1),
                        "seguridad_2": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.seguridad_2),
                        "seguridad_3": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.seguridad_3),
                        "seguridad_4": self._convertir_valor_aspecto_excel(row.IntranetVerificacionModel.seguridad_4),                        
                        "novedades": row.IntranetVerificacionModel.novedades,
                        "estado": row.IntranetVerificacionModel.estado,
                        "created_at": str(row.IntranetVerificacionModel.created_at)
                    }
                    for row in result
                ] if result else []
                return registros
            
            # Obtener el total de registros
            cant_registros = query.count()
            
            # Aplicar paginación
            new_offset = self.obtener_limit(limit, position)
            result = query.offset(new_offset).limit(limit).all()

            if result:
                for row in result:
                    response.append(
                        {
                            "id": row.IntranetVerificacionModel.id,
                            "lugar_inspeccion": row.nombre_lugar,
                            "responsable_verificacion": row.nombre_responsable,
                            "lugar_inspeccion_id": row.IntranetVerificacionModel.lugar_inspeccion_id,
                            "responsable_verificacion_id": row.IntranetVerificacionModel.responsable_verificacion_id,
                            "aspectos_1": self._convertir_valor_aspecto(row.IntranetVerificacionModel.aspectos_1),
                            "aspectos_2": self._convertir_valor_aspecto(row.IntranetVerificacionModel.aspectos_2),
                            "aspectos_3": self._convertir_valor_aspecto(row.IntranetVerificacionModel.aspectos_3),
                            "aspectos_4": self._convertir_valor_aspecto(row.IntranetVerificacionModel.aspectos_4),
                            "paredes_1": self._convertir_valor_aspecto(row.IntranetVerificacionModel.paredes_1),
                            "paredes_2": self._convertir_valor_aspecto(row.IntranetVerificacionModel.paredes_2),
                            "paredes_3": self._convertir_valor_aspecto(row.IntranetVerificacionModel.paredes_3),
                            "paredes_4": self._convertir_valor_aspecto(row.IntranetVerificacionModel.paredes_4),
                            "puertas_1": self._convertir_valor_aspecto(row.IntranetVerificacionModel.puertas_1),
                            "puertas_2": self._convertir_valor_aspecto(row.IntranetVerificacionModel.puertas_2),
                            "puertas_3": self._convertir_valor_aspecto(row.IntranetVerificacionModel.puertas_3),
                            "puertas_4": self._convertir_valor_aspecto(row.IntranetVerificacionModel.puertas_4),
                            "puertas_5": self._convertir_valor_aspecto(row.IntranetVerificacionModel.puertas_5),
                            "pisos_1": self._convertir_valor_aspecto(row.IntranetVerificacionModel.pisos_1),
                            "pisos_2": self._convertir_valor_aspecto(row.IntranetVerificacionModel.pisos_2),
                            "pisos_3": self._convertir_valor_aspecto(row.IntranetVerificacionModel.pisos_3),
                            "pisos_4": self._convertir_valor_aspecto(row.IntranetVerificacionModel.pisos_4),
                            "techo_1": self._convertir_valor_aspecto(row.IntranetVerificacionModel.techo_1),
                            "techo_2": self._convertir_valor_aspecto(row.IntranetVerificacionModel.techo_2),
                            "techo_3": self._convertir_valor_aspecto(row.IntranetVerificacionModel.techo_3),
                            "seguridad_1": self._convertir_valor_aspecto(row.IntranetVerificacionModel.seguridad_1),
                            "seguridad_2": self._convertir_valor_aspecto(row.IntranetVerificacionModel.seguridad_2),
                            "seguridad_3": self._convertir_valor_aspecto(row.IntranetVerificacionModel.seguridad_3),
                            "seguridad_4": self._convertir_valor_aspecto(row.IntranetVerificacionModel.seguridad_4),                        
                            "novedades": row.IntranetVerificacionModel.novedades,
                            "estado": row.IntranetVerificacionModel.estado,
                            "fecha_creacion": row.IntranetVerificacionModel.created_at.strftime("%Y-%m-%d %H:%M:%S") if row.IntranetVerificacionModel.created_at else None
                        }
                    )
            return {"registros": response, "cant_registros": cant_registros}
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Función que arma el limite de paginación
    def obtener_limit(self, limit: int, position: int):
        offset = (position - 1) * limit
        return offset

    # Query para obtener los lugares de inspección activos
    def obtener_lugares_inspeccion(self):
        try:
            response = []
            
            # Obtener lugares de inspección activos
            result = self.db.query(IntranetLugarInspeccionModel).filter(
                IntranetLugarInspeccionModel.estado == 1
            ).order_by(IntranetLugarInspeccionModel.nombre).all()
            
            if result:
                for row in result:
                    response.append({
                        "id": row.id,
                        "nombre": row.nombre
                    })
            
            return response
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para obtener los responsables por lugar de inspección con JOIN
    def obtener_responsables_por_lugar(self, lugar_id: int):
        try:
            response = []
            
            # Hacer JOIN entre las tablas para obtener los responsables del lugar
            result = self.db.query(
                IntranetResponsableVerificacionModel.id,
                IntranetResponsableVerificacionModel.nombre
            ).join(
                IntranetResponsableXLugarModel,
                IntranetResponsableXLugarModel.responsable_id == IntranetResponsableVerificacionModel.id
            ).filter(
                IntranetResponsableXLugarModel.lugar_id == lugar_id,
                IntranetResponsableXLugarModel.estado == 1,
                IntranetResponsableVerificacionModel.estado == 1
            ).order_by(IntranetResponsableVerificacionModel.nombre).all()
            
            if result:
                for row in result:
                    response.append({
                        "id": row.id,
                        "nombre": row.nombre
                    })
            
            return response
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para obtener los tipos de inspección
    def obtener_tipo_inspeccion(self):
        """ Retorna la lista de tipos de inspección activos """
        response = []
        try:
            result = self.db.query(
                IntranetTipoInspeccionModel.id,
                IntranetTipoInspeccionModel.nombre
            ).filter(
                IntranetTipoInspeccionModel.estado == 1
            ).all()
            
            if result:
                for row in result:
                    response.append({
                        "id": row.id,
                        "nombre": row.nombre
                    })
            
            return response
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para obtener los aspectos de carga según tipo de inspección
    def obtener_aspectos_por_tipo_inspeccion(self, tipo_inspeccion_id):
        """ Retorna la lista de aspectos agrupados por tipo/sección según el tipo de inspección """
        response = []
        try:
            # Hacer JOIN entre las tablas de relación, tipo de aspecto y aspectos de carga
            result = self.db.query(
                IntranetRelacionInspeccionAspectoModel.tipo_aspecto_id,
                IntranetTipoAspectosInfraestructuraModel.nombre.label('nombre_seccion'),
                IntranetAspectosCargaModel.id.label('aspecto_id'),
                IntranetAspectosCargaModel.nombre.label('nombre_aspecto')
            ).join(
                IntranetTipoAspectosInfraestructuraModel,
                IntranetRelacionInspeccionAspectoModel.tipo_aspecto_id == IntranetTipoAspectosInfraestructuraModel.id
            ).join(
                IntranetAspectosCargaModel,
                IntranetAspectosCargaModel.tipo_aspecto_id == IntranetTipoAspectosInfraestructuraModel.id
            ).filter(
                IntranetRelacionInspeccionAspectoModel.tipo_inspeccion_id == tipo_inspeccion_id,
                IntranetAspectosCargaModel.tipo_inspeccion == tipo_inspeccion_id,
                IntranetRelacionInspeccionAspectoModel.estado == 1,
                IntranetTipoAspectosInfraestructuraModel.estado == 1,
                IntranetAspectosCargaModel.estado == 1
            ).order_by(
                IntranetAspectosCargaModel.id
            ).all()
            
            # Agrupar por secciones
            secciones_dict = {}
            for row in result:
                seccion_id = row.tipo_aspecto_id
                
                if seccion_id not in secciones_dict:
                    secciones_dict[seccion_id] = {
                        "seccion_id": seccion_id,
                        "seccion_nombre": row.nombre_seccion,
                        "aspectos": []
                    }
                
                secciones_dict[seccion_id]["aspectos"].append({
                    "id": row.aspecto_id,
                    "nombre": row.nombre_aspecto
                })
            
            # Convertir el diccionario a lista
            response = list(secciones_dict.values())
            
            return response
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para guardar inspección de carga (dinámico)
    def guardar_carga(self, data: dict):
        """ 
        Guarda la inspección de carga con aspectos dinámicos e imágenes comprimidas.
        
        Args:
            data (dict): {
                "tipo_inspeccion_id": int,
                "lugar_inspeccion_id": int,
                "responsable_verificacion_id": int,
                "aspectos_generales_dinamicos": {"aspecto_1": 1, "aspecto_2": 0, ...},
                "imagenes": [{"nombre": str, "base64": str}, ...],
                "novedades": str
            }
        
        Returns:
            bool: True si se guardó correctamente
        """
        image_utils = ImageUtils()
        inspeccion_id = None
        
        try:
            # 1. Guardar el encabezado de la inspección
            datos_encabezado = {
                "tipo_inspeccion_id": data.get("tipo_inspeccion_id"),
                "novedades": data.get("novedades"),
                # Campos adicionales según tipo de inspección
                "numero_contenedor": data.get("numero_contenedor"),
                "numero_sello_seguridad": data.get("numero_sello_seguridad"),
                "documento_transporte": data.get("documento_transporte"),
                "empresa_transporte": data.get("empresa_transporte"),
                "placa_vehiculo": data.get("placa_vehiculo"),
                # Campos de aduana y responsable
                "aduana_id": data.get("aduana_id"),
                "responsable_aduana_id": data.get("responsable_aduana_id")
            }
            
            nueva_inspeccion = IntranetInspeccionCargaModel(datos_encabezado)
            self.db.add(nueva_inspeccion)
            self.db.flush()  # Para obtener el ID generado
            
            inspeccion_id = nueva_inspeccion.id
            
            # 2. Guardar los detalles de aspectos (dinámicos)
            aspectos_dinamicos = data.get("aspectos_generales_dinamicos", {})
            
            for key, valor in aspectos_dinamicos.items():
                # El key viene como "aspecto_123" donde 123 es el ID del aspecto
                if key.startswith("aspecto_") and valor is not None:
                    aspecto_id = int(key.replace("aspecto_", ""))
                    
                    datos_detalle = {
                        "inspeccion_carga_id": inspeccion_id,
                        "aspecto_id": aspecto_id,
                        "valor_seleccionado": int(valor)
                    }
                    
                    nuevo_detalle = IntranetInspeccionCargaDetalleModel(datos_detalle)
                    self.db.add(nuevo_detalle)
            
            # 3. Guardar las imágenes comprimidas
            imagenes = data.get("imagenes", [])
            
            for imagen in imagenes:
                if imagen.get("base64"):
                    try:
                        # Comprimir y guardar la imagen
                        resultado = image_utils.comprimir_y_guardar_imagen(
                            imagen.get("base64"),
                            imagen.get("nombre")
                        )
                        
                        # Guardar registro en la base de datos
                        datos_imagen = {
                            "inspeccion_carga_id": inspeccion_id,
                            "nombre_archivo": resultado["nombre_archivo"],
                            "ruta_archivo": resultado["ruta_archivo"]
                        }
                        
                        nueva_imagen = IntranetInspeccionCargaImagenModel(datos_imagen)
                        self.db.add(nueva_imagen)
                        
                    except Exception as img_ex:
                        print(f"Error al procesar imagen: {str(img_ex)}")
                        # Continuar con las demás imágenes si una falla
                        continue
            
            # 4. Confirmar la transacción
            self.db.commit()
            return True
            
        except Exception as ex:
            self.db.rollback()
            print(f"Error al guardar inspección de carga: {str(ex)}")
            
            # Si hubo error, intentar eliminar las imágenes ya guardadas
            if inspeccion_id:
                try:
                    imagenes_guardadas = self.db.query(IntranetInspeccionCargaImagenModel).filter(
                        IntranetInspeccionCargaImagenModel.inspeccion_carga_id == inspeccion_id
                    ).all()
                    
                    for img in imagenes_guardadas:
                        image_utils.eliminar_imagen(img.ruta_archivo)
                except:
                    pass
            
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para cargar datos de inspecciones de carga con paginación y filtros
    def cargar_datos_carga(self, data: dict):
        """ 
        Carga los registros de inspecciones de carga con filtros y paginación.
        Incluye detalles de aspectos e imágenes.
        """
        try:
            response = []
            
            tipo_inspeccion_id = data.get("tipo_inspeccion_id")
            fecha_desde = data.get("fecha_desde")
            fecha_hasta = data.get("fecha_hasta")
            limit = data.get("limit")
            position = data.get("position")
            
            # Query base para obtener inspecciones
            query = self.db.query(
                IntranetInspeccionCargaModel
            ).filter(
                IntranetInspeccionCargaModel.estado == 1
            )
            
            # Filtrar por tipo de inspección si se proporciona
            if tipo_inspeccion_id:
                query = query.filter(IntranetInspeccionCargaModel.tipo_inspeccion_id == tipo_inspeccion_id)
            
            # Aplicar filtro de fechas si existen
            if fecha_desde and fecha_hasta:
                if '-' in fecha_desde:
                    fecha_inicio = datetime.strptime(f"{fecha_desde} 00:00:00", "%Y-%m-%d %H:%M:%S")
                    fecha_fin = datetime.strptime(f"{fecha_hasta} 23:59:59", "%Y-%m-%d %H:%M:%S")
                else:
                    fecha_inicio = datetime.strptime(f"{fecha_desde} 00:00:00", "%Y%m%d %H:%M:%S")
                    fecha_fin = datetime.strptime(f"{fecha_hasta} 23:59:59", "%Y%m%d %H:%M:%S")
                query = query.filter(IntranetInspeccionCargaModel.created_at.between(fecha_inicio, fecha_fin))
            
            # Ordenar por fecha descendente
            query = query.order_by(IntranetInspeccionCargaModel.id.desc())
            
            # Obtener el total de registros
            cant_registros = query.count()
            
            # Aplicar paginación
            new_offset = self.obtener_limit(limit, position)
            inspecciones = query.offset(new_offset).limit(limit).all()
            
            # Para cada inspección, obtener sus detalles
            for inspeccion in inspecciones:
                # Obtener detalles de aspectos con nombres y secciones
                detalles_query = self.db.query(
                    IntranetInspeccionCargaDetalleModel.aspecto_id,
                    IntranetInspeccionCargaDetalleModel.valor_seleccionado,
                    IntranetAspectosCargaModel.nombre.label('aspecto_nombre'),
                    IntranetAspectosCargaModel.tipo_aspecto_id,
                    IntranetTipoAspectosInfraestructuraModel.nombre.label('seccion_nombre')
                ).join(
                    IntranetAspectosCargaModel,
                    IntranetInspeccionCargaDetalleModel.aspecto_id == IntranetAspectosCargaModel.id
                ).join(
                    IntranetTipoAspectosInfraestructuraModel,
                    IntranetAspectosCargaModel.tipo_aspecto_id == IntranetTipoAspectosInfraestructuraModel.id
                ).filter(
                    IntranetInspeccionCargaDetalleModel.inspeccion_carga_id == inspeccion.id,
                    IntranetInspeccionCargaDetalleModel.estado == 1
                ).order_by(
                    IntranetAspectosCargaModel.tipo_aspecto_id,
                    IntranetAspectosCargaModel.id
                ).all()
                
                # Agrupar aspectos por sección
                aspectos_agrupados = {}
                for detalle in detalles_query:
                    seccion_id = detalle.tipo_aspecto_id
                    
                    if seccion_id not in aspectos_agrupados:
                        aspectos_agrupados[seccion_id] = {
                            "seccion_id": seccion_id,
                            "seccion_nombre": detalle.seccion_nombre,
                            "aspectos": []
                        }
                    
                    aspectos_agrupados[seccion_id]["aspectos"].append({
                        "aspecto_id": detalle.aspecto_id,
                        "aspecto_nombre": detalle.aspecto_nombre,
                        "valor": self._convertir_valor_aspecto_excel(detalle.valor_seleccionado)
                    })
                
                # Obtener imágenes asociadas
                imagenes_query = self.db.query(
                    IntranetInspeccionCargaImagenModel
                ).filter(
                    IntranetInspeccionCargaImagenModel.inspeccion_carga_id == inspeccion.id,
                    IntranetInspeccionCargaImagenModel.estado == 1
                ).all()
                
                imagenes_list = [{
                    "id": img.id,
                    "nombre_archivo": img.nombre_archivo,
                    "ruta_archivo": img.ruta_archivo
                } for img in imagenes_query]
                
                # Obtener nombre del tipo de inspección
                tipo_inspeccion = self.db.query(IntranetTipoInspeccionModel).filter(
                    IntranetTipoInspeccionModel.id == inspeccion.tipo_inspeccion_id
                ).first()
                
                # Obtener nombre de aduana si existe
                aduana_nombre = None
                if inspeccion.aduana_id:
                    aduana = self.db.query(IntranetAduanasModel).filter(
                        IntranetAduanasModel.id == inspeccion.aduana_id
                    ).first()
                    aduana_nombre = aduana.nombre if aduana else None
                
                # Obtener nombre de responsable de aduana si existe
                responsable_aduana_nombre = None
                if inspeccion.responsable_aduana_id:
                    responsable = self.db.query(IntranetResponsableVerificacionModel).filter(
                        IntranetResponsableVerificacionModel.id == inspeccion.responsable_aduana_id
                    ).first()
                    responsable_aduana_nombre = responsable.nombre if responsable else None
                
                response.append({
                    "id": inspeccion.id,
                    "tipo_inspeccion_id": inspeccion.tipo_inspeccion_id,
                    "tipo_inspeccion_nombre": tipo_inspeccion.nombre if tipo_inspeccion else "N/A",
                    "novedades": inspeccion.novedades,
                    "fecha_creacion": inspeccion.created_at.strftime("%Y-%m-%d %H:%M:%S") if inspeccion.created_at else None,
                    # Campos adicionales según tipo de inspección
                    "numero_contenedor": inspeccion.numero_contenedor,
                    "numero_sello_seguridad": inspeccion.numero_sello_seguridad,
                    "documento_transporte": inspeccion.documento_transporte,
                    "empresa_transporte": inspeccion.empresa_transporte,
                    "placa_vehiculo": inspeccion.placa_vehiculo,
                    # Campos de aduana y responsable
                    "aduana_id": inspeccion.aduana_id,
                    "aduana_nombre": aduana_nombre,
                    "responsable_aduana_id": inspeccion.responsable_aduana_id,
                    "responsable_aduana_nombre": responsable_aduana_nombre,
                    "aspectos": list(aspectos_agrupados.values()),
                    "imagenes": imagenes_list
                })
            
            return {"registros": response, "cant_registros": cant_registros}
        except Exception as ex:
            print(f"Error en cargar_datos_carga: {str(ex)}")
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para obtener las aduanas activas
    def obtener_aduanas(self):
        """ Retorna la lista de aduanas activas """
        try:
            response = []
            
            # Usamos text() para hacer un CAST explícito del campo nombre
            result = self.db.query(IntranetAduanasModel).filter(
                IntranetAduanasModel.estado == 1
            ).all()
            
            if result:
                for row in result:
                    response.append({
                        "id": row.id,
                        "nombre": row.nombre
                    })
            
            return response
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para obtener los responsables por aduana con JOIN
    def obtener_responsables_por_aduana(self, aduana_id: int):
        """ Retorna la lista de responsables asociados a una aduana específica """
        try:
            response = []
            
            # Hacer JOIN entre las tablas para obtener los responsables de la aduana
            result = self.db.query(
                IntranetResponsableVerificacionModel.id,
                IntranetResponsableVerificacionModel.nombre
            ).join(
                IntranetResponsableXAduanasModel,
                IntranetResponsableXAduanasModel.responsable_id == IntranetResponsableVerificacionModel.id
            ).filter(
                IntranetResponsableXAduanasModel.aduana_id == aduana_id,
                IntranetResponsableXAduanasModel.estado == 1,
                IntranetResponsableVerificacionModel.estado == 1
            ).order_by(IntranetResponsableVerificacionModel.nombre).all()
            
            if result:
                for row in result:
                    response.append({
                        "id": row.id,
                        "nombre": row.nombre
                    })
            
            return response
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()
