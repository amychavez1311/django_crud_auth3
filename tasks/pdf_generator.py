"""
Generador de PDFs de hojas de vida usando ReportLab
Incluye referencias a certificados en el PDF
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import tempfile
from django.core.files.storage import default_storage
from django.conf import settings


class CVPDFGenerator:
    """Generador de PDFs para hojas de vida con ReportLab"""
    
    def __init__(self, datos_personales):
        self.datos = datos_personales
        self.user = datos_personales.user
        self.story = []
        self.styles = getSampleStyleSheet()
        self.certificados_para_incrustar = []  # Lista de PDFs a incrustar
        self.temp_files = []  # Lista de archivos temporales para limpiar
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crea estilos personalizados para el PDF"""
        # Estilo para títulos de secciones
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            spaceBefore=12,
            borderBottom=1,
            borderColor=colors.HexColor('#1a5490'),
            paddingBottom=6
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            bold=True
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            alignment=TA_JUSTIFY
        ))
    
    def _download_file_from_storage(self, file_field):
        """
        Descarga un archivo desde el storage (local o Azure) y retorna una ruta temporal.
        Funciona tanto con archivos locales como con Azure Storage.
        
        Args:
            file_field: Campo de archivo de Django (ImageField, FileField, etc.)
            
        Returns:
            tuple: (ruta_temporal, content_bytes) - la ruta y los bytes del archivo
        """
        try:
            # Si el archivo está vacío
            if not file_field or not file_field.name:
                return None, None
            
            content = None
            
            # Intentar descargar como archivo local primero
            try:
                # Si tiene atributo path, es archivo local
                if hasattr(file_field, 'path'):
                    file_path = file_field.path
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            content = f.read()
            except (AttributeError, OSError):
                pass
            
            # Si no se obtuvo como local, intentar desde storage (Azure)
            if content is None:
                try:
                    # Usar Django's storage API (funciona con cualquier backend)
                    content = file_field.read()
                except Exception as e:
                    print(f"Error leyendo archivo desde storage: {e}")
                    return None, None
            
            # Crear archivo temporal
            if content:
                # Obtener extensión del archivo
                _, ext = os.path.splitext(file_field.name)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                temp_path = temp_file.name
                temp_file.write(content)
                temp_file.close()
                
                # Guardar path temporal para limpieza posterior
                self.temp_files.append(temp_path)
                
                return temp_path, content
        
        except Exception as e:
            print(f"Error descargando archivo desde storage: {e}")
        
        return None, None
    
    def _add_header(self):
        """Añade encabezado con datos personales e imagen de perfil"""
        # Crear tabla con imagen y datos de contacto
        left_col = []
        
        # Agregar imagen de perfil si existe
        if self.datos.fotoperfil:
            try:
                # Descargar imagen desde storage (local o Azure)
                temp_path, _ = self._download_file_from_storage(self.datos.fotoperfil)
                
                if temp_path and os.path.exists(temp_path):
                    try:
                        img = Image(temp_path, width=1.2*inch, height=1.2*inch)
                        left_col.append(img)
                    except Exception as e:
                        print(f"Error creando imagen para PDF: {e}")
            
            except Exception as e:
                print(f"Error cargando foto de perfil: {e}")
        
        # Derecha: Nombre y datos de contacto
        right_col = []
        
        # Título con nombre completo
        nombre_completo = f"{self.datos.nombres} {self.datos.apellidos}".upper()
        title = Paragraph(f"<b>{nombre_completo}</b>", self.styles['Title'])
        right_col.append(title)
        
        # Descripción del perfil
        if self.datos.descripcionperfil:
            descripcion = Paragraph(
                f"<i>{self.datos.descripcionperfil}</i>",
                self.styles['NormalText']
            )
            right_col.append(descripcion)
        
        right_col.append(Spacer(1, 0.08*inch))
        
        # Datos de contacto
        contact_info = []
        if self.datos.telefonoconvencional:
            contact_info.append(f"<b>Teléfono:</b> {self.datos.telefonoconvencional}")
        if self.datos.telefonofijo:
            contact_info.append(f"<b>Teléfono Fijo:</b> {self.datos.telefonofijo}")
        if self.user.email:
            contact_info.append(f"<b>Email:</b> {self.user.email}")
        if self.datos.sitioweb:
            contact_info.append(f"<b>Sitio Web:</b> {self.datos.sitioweb}")
        
        for info in contact_info:
            right_col.append(Paragraph(info, self.styles['Normal']))
        
        # Crear tabla del encabezado
        header_table = Table([[left_col, right_col]], colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(header_table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_datos_personales(self):
        """Añade sección de datos personales"""
        self.story.append(Paragraph("DATOS PERSONALES", self.styles['SectionTitle']))
        
        datos = [
            ['Cédula de Identidad:', self.datos.numerocedula],
            ['Sexo:', 'Hombre' if self.datos.sexo == 'H' else 'Mujer' if self.datos.sexo else 'No especificado'],
            ['Fecha de Nacimiento:', str(self.datos.fechanacimiento) if self.datos.fechanacimiento else 'N/A'],
            ['Nacionalidad:', self.datos.nacionalidad or 'N/A'],
            ['Lugar de Nacimiento:', self.datos.lugarnacimiento or 'N/A'],
            ['Estado Civil:', self.datos.estadocivil or 'N/A'],
            ['Licencia de Conducir:', self.datos.licenciaconducir or 'N/A'],
        ]
        
        direccion_data = []
        if self.datos.direcciondomiciliaria:
            direccion_data.append(['Dirección Domiciliaria:', self.datos.direcciondomiciliaria])
        if self.datos.direcciontrabajo:
            direccion_data.append(['Dirección de Trabajo:', self.datos.direcciontrabajo])
        
        tabla_datos = Table(datos + direccion_data, colWidths=[2*inch, 4.5*inch])
        tabla_datos.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        
        self.story.append(tabla_datos)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_experiencia_laboral(self):
        """Añade sección de experiencia laboral"""
        experiencias = self.datos.experiencias_laborales.filter(activo=True)
        
        if not experiencias.exists():
            return
        
        self.story.append(Paragraph("EXPERIENCIA LABORAL", self.styles['SectionTitle']))
        
        for exp in experiencias:
            # Cargo y empresa
            exp_title = f"<b>{exp.cargodesempenado}</b>"
            if exp.nombreempresa:
                exp_title += f" - {exp.nombreempresa}"
            self.story.append(Paragraph(exp_title, self.styles['NormalText']))
            
            # Fechas y lugar
            fecha_inicio = exp.fechainiciogestion.strftime('%b %Y') if exp.fechainiciogestion else ''
            fecha_fin = exp.fechafingestion.strftime('%b %Y') if exp.fechafingestion else 'Presente'
            periodos = f"<i>{fecha_inicio} - {fecha_fin}</i>"
            if exp.lugarempresa:
                periodos += f" | {exp.lugarempresa}"
            self.story.append(Paragraph(periodos, self.styles['Normal']))
            
            # Descripción
            if exp.descripcionfunciones:
                self.story.append(Paragraph(
                    exp.descripcionfunciones,
                    self.styles['NormalText']
                ))
            
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_reconocimientos(self):
        """Añade sección de reconocimientos con imágenes de certificados"""
        reconocimientos = self.datos.reconocimientos.filter(activo=True)
        
        if not reconocimientos.exists():
            return
        
        self.story.append(Paragraph("RECONOCIMIENTOS", self.styles['SectionTitle']))
        
        for reco in reconocimientos:
            # Tipo y entidad
            titulo = f"<b>{reco.get_tiporeconocimiento_display()}</b> - {reco.entidadpatrocinadora}"
            self.story.append(Paragraph(titulo, self.styles['NormalText']))
            
            # Fecha
            if reco.fechareconocimiento:
                fecha = reco.fechareconocimiento.strftime('%d de %B de %Y')
                self.story.append(Paragraph(f"<i>Fecha: {fecha}</i>", self.styles['Normal']))
            
            # Descripción
            if reco.descripcionreconocimiento:
                self.story.append(Paragraph(
                    reco.descripcionreconocimiento,
                    self.styles['NormalText']
                ))
            
            # Certificado
            if reco.certificado:
                cert_name = os.path.basename(reco.certificado.name)
                
                # Verificar que sea un PDF
                if cert_name.lower().endswith('.pdf'):
                    self.certificados_para_incrustar.append({
                        'file_field': reco.certificado,
                        'titulo': f"{reco.get_tiporeconocimiento_display()} - {reco.entidadpatrocinadora}"
                    })
                    self.story.append(Paragraph(
                        f"<b>📎 Certificado:</b> {cert_name} (Incrustado abajo)",
                        self.styles['Normal']
                    ))
                else:
                    self.story.append(Paragraph(
                        f"<b>📎 Certificado:</b> {cert_name}",
                        self.styles['Normal']
                    ))
            
            self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_cursos(self):
        """Añade sección de cursos realizados con imágenes de certificados"""
        cursos = self.datos.cursos_realizados.filter(activo=True)
        
        if not cursos.exists():
            return
        
        self.story.append(Paragraph("CURSOS Y CAPACITACIONES", self.styles['SectionTitle']))
        
        for curso in cursos:
            # Nombre del curso
            titulo = f"<b>{curso.nombrecurso}</b>"
            self.story.append(Paragraph(titulo, self.styles['NormalText']))
            
            # Entidad y fechas
            entidad = f"<i>{curso.entidadpatrocinadora}</i>"
            if curso.fechainicio or curso.fechafin:
                fecha_inicio = curso.fechainicio.strftime('%b %Y') if curso.fechainicio else ''
                fecha_fin = curso.fechafin.strftime('%b %Y') if curso.fechafin else ''
                fechas = f" | {fecha_inicio} - {fecha_fin}"
                entidad += fechas
            self.story.append(Paragraph(entidad, self.styles['Normal']))
            
            # Horas
            if curso.totalhoras:
                self.story.append(Paragraph(f"Horas: {curso.totalhoras}", self.styles['Normal']))
            
            # Descripción
            if curso.descripcioncurso:
                self.story.append(Paragraph(
                    curso.descripcioncurso,
                    self.styles['NormalText']
                ))
            
            # Certificado
            if curso.certificado:
                cert_name = os.path.basename(curso.certificado.name)
                
                # Verificar que sea un PDF
                if cert_name.lower().endswith('.pdf'):
                    self.certificados_para_incrustar.append({
                        'file_field': curso.certificado,
                        'titulo': f"Curso: {curso.nombrecurso}"
                    })
                    self.story.append(Paragraph(
                        f"<b>📎 Certificado:</b> {cert_name} (Incrustado abajo)",
                        self.styles['Normal']
                    ))
                else:
                    self.story.append(Paragraph(
                        f"<b>📎 Certificado:</b> {cert_name}",
                        self.styles['Normal']
                    ))
            
                        self.styles['Normal']
                    ))
            
            self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_productos_academicos(self):
        """Añade sección de productos académicos"""
        productos = self.datos.productos_academicos.filter(activo=True)
        
        if not productos.exists():
            return
        
        self.story.append(Paragraph("PRODUCTOS ACADÉMICOS", self.styles['SectionTitle']))
        
        for prod in productos:
            titulo = f"<b>{prod.nombrerecurso}</b> ({prod.clasificador})"
            self.story.append(Paragraph(titulo, self.styles['NormalText']))
            
            if prod.descripcion:
                self.story.append(Paragraph(prod.descripcion, self.styles['Normal']))
            
            self.story.append(Spacer(1, 0.05*inch))
        
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_footer(self):
        """Añade pie de página"""
        self.story.append(Spacer(1, 0.15*inch))
        fecha_generacion = datetime.now().strftime('%d de %B de %Y')
        footer = Paragraph(
            f"<i>Generado el: {fecha_generacion}</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        self.story.append(footer)
    
    def generate(self):
        """
        Genera el PDF y lo retorna como BytesIO
        Incluye certificados incrustados al final
        
        Returns:
            BytesIO con el contenido del PDF
        """
        try:
            # Crear documento en memoria
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Construir el documento con secciones dinámicas
            self._add_header()
            self._add_datos_personales()
            
            # Solo agregar secciones que tengan datos
            if self.datos.experiencias_laborales.filter(activo=True).exists():
                self._add_experiencia_laboral()
            
            if self.datos.reconocimientos.filter(activo=True).exists():
                self._add_reconocimientos()
            
            if self.datos.cursos_realizados.filter(activo=True).exists():
                self._add_cursos()
            
            if self.datos.productos_academicos.filter(activo=True).exists():
                self._add_productos_academicos()
            
            self._add_footer()
            
            # Generar el PDF principal
            doc.build(self.story)
            
            # Si hay certificados, incrustarlos
            if self.certificados_para_incrustar:
                pdf_buffer.seek(0)
                pdf_buffer = self._incrustar_certificados(pdf_buffer)
            
            # Limpiar archivos temporales (imágenes descargadas de Azure)
            if hasattr(self, 'temp_files'):
                for temp_file in self.temp_files:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
            
            # Retornar al inicio del buffer
            pdf_buffer.seek(0)
            return pdf_buffer
        
        except Exception as e:
            print(f"Error generando PDF: {e}")
            # Limpiar temporales en caso de error
            if hasattr(self, 'temp_files'):
                for temp_file in self.temp_files:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
            return None
    
    def _incrustar_certificados(self, pdf_principal_buffer):
        """
        Incrustra los PDFs de certificados al final del PDF principal.
        Funciona automáticamente con archivos locales y Azure Storage.
        """
        try:
            # Lector del PDF principal
            pdf_reader = PdfReader(pdf_principal_buffer)
            writer = PdfWriter()
            
            # Copiar todas las páginas del PDF principal
            for page_num in range(len(pdf_reader.pages)):
                writer.add_page(pdf_reader.pages[page_num])
            
            # Agregar los certificados
            for cert_info in self.certificados_para_incrustar:
                # Obtener el objeto del archivo (puede tener 'url' o 'path')
                cert_field = cert_info.get('file_field')
                cert_titulo = cert_info.get('titulo', 'Certificado')
                
                if not cert_field:
                    continue
                
                try:
                    # Descargar el certificado desde storage (local o Azure)
                    temp_path, content = self._download_file_from_storage(cert_field)
                    
                    if not temp_path or not content:
                        print(f"No se pudo descargar certificado: {cert_titulo}")
                        continue
                    
                    # Leer el PDF descargado
                    try:
                        cert_buffer = BytesIO(content)
                        cert_buffer.seek(0)
                        cert_reader = PdfReader(cert_buffer)
                        
                        # Agregar todas las páginas del certificado
                        for page_num in range(len(cert_reader.pages)):
                            writer.add_page(cert_reader.pages[page_num])
                        
                        print(f"Certificado incrustado: {cert_titulo}")
                    
                    except Exception as e:
                        print(f"Error leyendo PDF de certificado: {e}")
                        continue
                
                except Exception as e:
                    print(f"Error procesando certificado {cert_titulo}: {e}")
                    continue
            
            # Crear un nuevo buffer con el PDF combinado
            output_buffer = BytesIO()
            writer.write(output_buffer)
            
            return output_buffer
        
        except Exception as e:
            print(f"Error incrustando certificados: {e}")
            return pdf_principal_buffer
