"""
Utilidades para manejo de fechas y horas con zona horaria de Colombia
"""
import pytz
from datetime import datetime

# Zona horaria de Colombia (UTC-5)
COLOMBIA_TZ = pytz.timezone('America/Bogota')

def get_colombia_time():
    """
    Retorna la fecha y hora actual de Colombia (UTC-5)
    sin información de timezone para compatibilidad con la base de datos
    """
    return datetime.now(COLOMBIA_TZ).replace(tzinfo=None)
