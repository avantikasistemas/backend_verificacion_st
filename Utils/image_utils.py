import os
import base64
import uuid
from PIL import Image
from io import BytesIO
from datetime import datetime

class ImageUtils:
    """
    Utilidad para manejar imágenes: compresión, conversión y guardado.
    """
    
    def __init__(self, upload_folder="Uploads"):
        self.upload_folder = upload_folder
        self.max_width = 1920  # Ancho máximo de la imagen
        self.max_height = 1080  # Alto máximo de la imagen
        self.quality = 85  # Calidad de compresión JPEG (0-100)
        
        # Crear la carpeta Uploads si no existe
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def comprimir_y_guardar_imagen(self, base64_string, nombre_original=None):
        """
        Comprime una imagen en base64 y la guarda en el servidor.
        
        Args:
            base64_string (str): String base64 de la imagen
            nombre_original (str): Nombre original del archivo (opcional)
            
        Returns:
            dict: {
                "nombre_archivo": nombre del archivo guardado,
                "ruta_archivo": ruta relativa del archivo,
                "ruta_completa": ruta absoluta del archivo
            }
        """
        try:
            # Remover el prefijo data:image/...;base64, si existe
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decodificar base64
            image_data = base64.b64decode(base64_string)
            
            # Abrir la imagen con Pillow
            image = Image.open(BytesIO(image_data))
            
            # Convertir a RGB si es necesario (para PNG con transparencia)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Crear fondo blanco
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionar si excede las dimensiones máximas
            if image.width > self.max_width or image.height > self.max_height:
                image.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
            
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            extension = "jpg"
            
            if nombre_original:
                # Obtener extensión del nombre original si existe
                nombre_base = os.path.splitext(nombre_original)[0]
                nombre_archivo = f"{nombre_base}_{timestamp}_{unique_id}.{extension}"
            else:
                nombre_archivo = f"imagen_{timestamp}_{unique_id}.{extension}"
            
            # Guardar directamente en la carpeta Uploads sin subcarpetas
            ruta_completa = os.path.join(self.upload_folder, nombre_archivo)
            
            # Guardar la imagen comprimida
            image.save(ruta_completa, "JPEG", quality=self.quality, optimize=True)
            
            # Ruta relativa para guardar en base de datos (solo el nombre del archivo)
            ruta_relativa = nombre_archivo
            
            return {
                "nombre_archivo": nombre_archivo,
                "ruta_archivo": ruta_relativa,
                "ruta_completa": ruta_completa
            }
            
        except Exception as ex:
            print(f"Error al comprimir y guardar imagen: {str(ex)}")
            raise Exception(f"Error al procesar imagen: {str(ex)}")
    
    def eliminar_imagen(self, ruta_relativa):
        """
        Elimina una imagen del servidor.
        
        Args:
            ruta_relativa (str): Ruta relativa de la imagen (nombre del archivo)
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            # Como ahora guardamos directamente en Uploads, la ruta_relativa es solo el nombre del archivo
            ruta_completa = os.path.join(self.upload_folder, ruta_relativa)
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)
                return True
            return False
        except Exception as ex:
            print(f"Error al eliminar imagen: {str(ex)}")
            return False
    
    def obtener_ruta_completa(self, ruta_relativa):
        """
        Obtiene la ruta completa de una imagen.
        
        Args:
            ruta_relativa (str): Ruta relativa de la imagen
            
        Returns:
            str: Ruta completa de la imagen
        """
        return os.path.join(self.upload_folder, ruta_relativa)
    
    def save_base64_image(self, base64_string, nombre_original=None):
        """
        Guarda una imagen desde base64 (método de compatibilidad).
        
        Args:
            base64_string (str): String base64 de la imagen
            nombre_original (str): Nombre original del archivo (opcional)
            
        Returns:
            tuple: (nombre_archivo, ruta_archivo)
        """
        resultado = self.comprimir_y_guardar_imagen(base64_string, nombre_original)
        return resultado["nombre_archivo"], resultado["ruta_archivo"]
