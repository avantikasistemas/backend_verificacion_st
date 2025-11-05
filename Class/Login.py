from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Config.jwt_config import create_access_token

class Login:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función para cargar los datos registrados
    def login(self, data: dict):
        """ Api que realiza el login de usuario. """
        try:
            # Validar que vengan los campos requeridos
            usuario = data["usuario"]
            clave = data["clave"]

            if not usuario:
                raise CustomException("El campo usuario es requerido")
            
            if not clave:
                raise CustomException("El campo clave es requerido")

            usuario = usuario.strip().upper()  # Convertir a mayúsculas
            clave = clave.strip().upper()  # Convertir a mayúsculas

            # Validar usuario usando querys.py
            user_data = self.querys.validar_login(usuario, clave)
            
            # Crear token JWT
            token_data = {
                "usuario": user_data["usuario"],
                "nombre": user_data["nombre"],
                "email": user_data["email"],
            }
            
            access_token = create_access_token(data=token_data)
            
            # Preparar respuesta
            response_data = {
                "usuario": user_data["usuario"],
                "nombre": user_data["nombre"],
                "email": user_data["email"],
                "token": access_token
            }
            
            # Retornar la información
            return self.tools.output(200, "Login exitoso", response_data)

        except CustomException as e:
            print(f"Error al realizar login: {e}")
            raise CustomException(f"{e}")
        except Exception as e:
            print(f"Error inesperado en login: {str(e)}")
            raise CustomException("Error al procesar la solicitud de login")
