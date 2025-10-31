from Utils.tools import Tools, CustomException
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
