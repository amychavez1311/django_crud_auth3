"""
Utilidad para convertir archivos PDF a imágenes PNG
Utilizado para incrustar certificados en hojas de vida PDF
"""

from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
from io import BytesIO


class PDFtoImageConverter:
    """Convierte PDFs a imágenes PNG de alta calidad"""
    
    @staticmethod
    def convert_pdf_to_image(pdf_path, dpi=150, max_pages=1):
        """
        Convierte un archivo PDF a una imagen PNG
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            dpi (int): Resolución de la imagen (default 150)
            max_pages (int): Número máximo de páginas a convertir (default 1)
            
        Returns:
            BytesIO con la imagen PNG convertida o None si hay error
        """
        try:
            if not os.path.exists(pdf_path):
                return None
            
            # Convertir PDF a imágenes
            images = convert_from_path(
                pdf_path, 
                dpi=dpi,
                first_page=1,
                last_page=max_pages
            )
            
            if not images:
                return None
            
            # Tomar la primera página
            image = images[0]
            
            # Convertir a PNG
            png_buffer = BytesIO()
            image.save(png_buffer, format='PNG')
            png_buffer.seek(0)
            
            return png_buffer
            
        except Exception as e:
            print(f"Error convirtiendo PDF a imagen: {e}")
            return None
    
    @staticmethod
    def convert_pdf_to_file(pdf_path, output_path, dpi=150):
        """
        Convierte un PDF a imagen PNG y lo guarda en archivo
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            output_path (str): Ruta donde guardar la imagen PNG
            dpi (int): Resolución de la imagen (default 150)
            
        Returns:
            bool: True si se convirtió exitosamente, False en caso contrario
        """
        try:
            if not os.path.exists(pdf_path):
                return False
            
            # Convertir PDF a imágenes
            images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
            
            if not images:
                return False
            
            # Guardar la primera página
            images[0].save(output_path, 'PNG')
            return True
            
        except Exception as e:
            print(f"Error convirtiendo PDF: {e}")
            return False
    
    @staticmethod
    def get_image_from_pdf(pdf_path, width=None, height=None):
        """
        Obtiene una imagen PIL del PDF
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            width (int): Ancho deseado (optional)
            height (int): Alto deseado (optional)
            
        Returns:
            Image o None si hay error
        """
        try:
            if not os.path.exists(pdf_path):
                return None
            
            images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1)
            
            if not images:
                return None
            
            image = images[0]
            
            # Redimensionar si se especifican dimensiones
            if width and height:
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            print(f"Error obteniendo imagen del PDF: {e}")
            return None
