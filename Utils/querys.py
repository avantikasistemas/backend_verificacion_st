from Utils.tools import Tools, CustomException
from sqlalchemy import text
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from Utils.constants import CAMPOS_MONETARIOS

class Querys:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.query_params = dict()

    # Query para guardar verificacion
    def guardar_verificacion(self, data: dict):
        try:
            sql = """
                INSERT INTO dbo.intranet_verificacion_items (usuario, puertas, ventanas, iluminacion_oficinas, barreras_interiores, estado_camaras, novedades)
                VALUES (:usuario, :puertas, :ventanas, :iluminacion_oficinas, :barreras_interiores, :estado_camaras, :novedades)
            """
            self.db.execute(
                text(sql), 
                {
                    "usuario": data["usuario"],
                    "puertas": 1 if data["puertas"] else 0,
                    "ventanas": 1 if data["ventanas"] else 0,
                    "iluminacion_oficinas": 1 if data["iluminacion_oficinas"] else 0,
                    "barreras_interiores": 1 if data["barreras_interiores"] else 0,
                    "estado_camaras": 1 if data["estado_camaras"] else 0,
                    "novedades": data["novedades"]
                }
            )
            self.db.commit()
            return True
        except Exception as ex:
            print(str(ex))
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
            
            if flag_excel:
                sql = """
                    SELECT * FROM dbo.intranet_verificacion_items
                """
            else:
                sql = """
                    SELECT *, COUNT(*) OVER() AS total_registros FROM dbo.intranet_verificacion_items
                """
            
            if fecha_desde and fecha_hasta:
                sql = self.add_fecha_query(
                    sql, 
                    fecha_desde, 
                    fecha_hasta
                )
                
            if flag_excel:
                sql += " ORDER BY id DESC;"
                result = self.db.execute(text(sql), self.query_params).fetchall()
                registros = [dict((row._mapping) ) for row in result] if result else []
                return registros
            
            new_offset = self.obtener_limit(limit, position)
            self.query_params.update({"offset": new_offset, "limit": limit})
            sql += " ORDER BY id DESC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;"

            if self.query_params:
                result = self.db.execute(text(sql), self.query_params).fetchall()
            else:
                result = self.db.execute(text(sql)).fetchall()

            if result:
                cant_registros = result[0].total_registros
                for row in result:
                    response.append(
                        {
                            "id": row.id,
                            "usuario": row.usuario,
                            "puertas": "✔" if row.puertas == 1 else "✖",
                            "ventanas": "✔" if row.ventanas == 1 else "✖",
                            "iluminacion_oficinas": "✔" if row.iluminacion_oficinas == 1 else "✖",
                            "barreras_interiores": "✔" if row.barreras_interiores == 1 else "✖",
                            "estado_camaras": "✔" if row.estado_camaras == 1 else "✖",
                            "novedades": row.novedades,
                            "fecha_creacion": row.created_at.strftime("%Y-%m-%d %H:%M:%S") if row.created_at else None
                        }
                    )
            return {"registros": response, "cant_registros": cant_registros}
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query que complementa la inicial que filtra por fechas
    def add_fecha_query(self, sql, fecha_desde, fecha_hasta):
        sql = sql + " WHERE created_at BETWEEN :fecha_desde AND :fecha_hasta"
        self.query_params.update({"fecha_desde": f"{fecha_desde} 00:00:00", "fecha_hasta": f"{fecha_hasta} 23:59:59"})
        return sql

    # Función que arma el limite de paginación
    def obtener_limit(self, limit: int, position: int):
        offset = (position - 1) * limit
        return offset
