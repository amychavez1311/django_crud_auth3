"""
Generador PROFESIONAL de PDFs para CV
Diseño moderno, elegante y ATS-friendly
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, 
                                Spacer, PageBreak, Image, HRFlowable, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import tempfile
from django.core.files.storage import default_storage


class CVPDFGenerator:
    """Generador de PDFs profesionales para CV con diseño moderno"""
    
    # Paleta de colores profesional
    PRIMARY_COLOR = colors.HexColor('#2563EB')  # Azul profesional
    SECONDARY_COLOR = colors.HexColor('#64748B')  # Gris azulado
    ACCENT_COLOR = colors.HexColor('#10B981')  # Verde elegante
    DARK_TEXT = colors.HexColor('#1E293B')  # Casi negro
    LIGHT_TEXT = colors.HexColor('#64748B')  # Gris claro
    BACKGROUND = colors.HexColor('#F8FAFC')  # Fondo suave
    
    def __init__(self, datos_personales):
        self.datos = datos_personales
        self.user = datos_personales.user
        self.story = []
        self.styles = getSampleStyleSheet()
        self.certificados_para_incrustar = []
        self.temp_files = []
        self._create_modern_styles()
    
    def _create_modern_styles(self):
        """Crea estilos modernos y profesionales"""
        
        # Nombre principal - Grande y elegante
        self.styles.add(ParagraphStyle(
            name='MainName',
            parent=self.styles['Title'],
            fontSize=28,
            textColor=self.DARK_TEXT,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=4,
            leading=32
        ))
        
        # Título profesional
        self.styles.add(ParagraphStyle(
            name='ProfessionalTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=self.PRIMARY_COLOR,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            leading=16
        ))
        
        # Títulos de sección - Modernos con barra lateral
        self.styles.add(ParagraphStyle(
            name='ModernSection',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.PRIMARY_COLOR,
            fontName='Helvetica-Bold',
            spaceAfter=8,
            spaceBefore=20,
            leftIndent=0,
            leading=20
        ))
        
        # Subtítulos de posición/empresa
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.DARK_TEXT,
            fontName='Helvetica-Bold',
            spaceAfter=3,
            leading=14
        ))
        
        # Empresa/Institución
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.SECONDARY_COLOR,
            fontName='Helvetica-Oblique',
            spaceAfter=4,
            leading=13
        ))
        
        # Fechas
        self.styles.add(ParagraphStyle(
            name='DateStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.LIGHT_TEXT,
            fontName='Helvetica',
            spaceAfter=6,
            leading=11
        ))
        
        # Texto descriptivo
        self.styles.add(ParagraphStyle(
            name='Description',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.DARK_TEXT,
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=13,
            leftIndent=0
        ))
        
        # Información de contacto
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.SECONDARY_COLOR,
            fontName='Helvetica',
            spaceAfter=2,
            leading=12
        ))
        
        # Etiquetas/badges
        self.styles.add(ParagraphStyle(
            name='Badge',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.PRIMARY_COLOR,
            fontName='Helvetica-Bold',
            spaceAfter=4
        ))
    
    def _download_file_from_storage(self, file_field):
        """Descarga archivo desde storage (local o Azure)"""
        try:
            if not file_field or not file_field.name:
                return None, None
            
            content = None
            original_name = str(file_field.name)
            norm_name = original_name.replace('\\', '/').lstrip('/')
            
            candidates = [norm_name]
            
            if ':' in norm_name:
                after_drive = norm_name.split(':', 1)[1].lstrip('/')
                candidates.append(after_drive)
            
            if 'media/' in norm_name:
                after_media = norm_name.split('media/', 1)[1]
                candidates.append(after_media)
            
            candidates.append(os.path.basename(norm_name))
            
            opened = False
            last_err = None
            for name in candidates:
                try:
                    with default_storage.open(name, 'rb') as f:
                        content = f.read()
                        opened = True
                        break
                except Exception as e:
                    last_err = e
                    continue
            
            if not opened:
                return None, None
            
            if content:
                _, ext = os.path.splitext(os.path.basename(norm_name))
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                temp_path = temp_file.name
                temp_file.write(content)
                temp_file.close()
                self.temp_files.append(temp_path)
                return temp_path, content
        
        except Exception as e:
            print(f"Error descargando archivo: {e}")
        
        return None, None
    
    def _add_modern_header(self):
        """Añade encabezado moderno con foto y datos de contacto"""
        
        # Contenedores para las dos columnas
        left_content = []
        right_content = []
        
        # COLUMNA IZQUIERDA: Foto de perfil circular (si existe)
        if self.datos.fotoperfil:
            try:
                temp_path, _ = self._download_file_from_storage(self.datos.fotoperfil)
                if temp_path and os.path.exists(temp_path):
                    try:
                        # Imagen más grande y con mejor calidad
                        img = Image(temp_path, width=1.8*inch, height=1.8*inch)
                        left_content.append(img)
                    except Exception as e:
                        print(f"Error con imagen: {e}")
            except Exception as e:
                print(f"Error cargando foto: {e}")
        
        # COLUMNA DERECHA: Información principal
        nombre_completo = f"{self.datos.nombres} {self.datos.apellidos}".upper()
        right_content.append(Paragraph(nombre_completo, self.styles['MainName']))
        
        # Descripción profesional
        if self.datos.descripcionperfil:
            right_content.append(Paragraph(
                self.datos.descripcionperfil,
                self.styles['ProfessionalTitle']
            ))
        
        right_content.append(Spacer(1, 0.15*inch))
        
        # Información de contacto en formato compacto y elegante
        contact_items = []
        
        if self.datos.telefonoconvencional:
            contact_items.append(f"📱 {self.datos.telefonoconvencional}")
        
        if self.user.email:
            contact_items.append(f"✉️ {self.user.email}")
        
        if self.datos.sitioweb:
            contact_items.append(f"🌐 {self.datos.sitioweb}")
        
        if self.datos.ciudad:
            contact_items.append(f"📍 {self.datos.ciudad}, {self.datos.pais or 'Ecuador'}")
        
        for item in contact_items:
            right_content.append(Paragraph(item, self.styles['ContactInfo']))
        
        # Crear tabla con las dos columnas
        if left_content:
            header_table = Table(
                [[left_content, right_content]], 
                colWidths=[2*inch, 4.5*inch]
            )
        else:
            header_table = Table(
                [[right_content]], 
                colWidths=[6.5*inch]
            )
        
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        self.story.append(header_table)
        
        # Línea divisoria elegante
        self.story.append(Spacer(1, 0.15*inch))
        self.story.append(HRFlowable(
            width="100%",
            thickness=2,
            color=self.PRIMARY_COLOR,
            spaceBefore=5,
            spaceAfter=15
        ))
    
    def _add_section_title(self, title, icon="●"):
        """Añade título de sección con diseño moderno"""
        section_title = f"<b>{icon} {title.upper()}</b>"
        self.story.append(Paragraph(section_title, self.styles['ModernSection']))
        
        # Línea debajo del título
        self.story.append(HRFlowable(
            width="20%",
            thickness=3,
            color=self.ACCENT_COLOR,
            spaceBefore=2,
            spaceAfter=12,
            hAlign='LEFT'
        ))
    
    def _add_experience_item(self, cargo, empresa, fecha_inicio, fecha_fin, descripcion):
        """Añade un elemento de experiencia con diseño profesional"""
        items = []
        
        # Cargo en negrita
        items.append(Paragraph(f"<b>{cargo}</b>", self.styles['JobTitle']))
        
        # Empresa
        if empresa:
            items.append(Paragraph(empresa, self.styles['Company']))
        
        # Fechas
        if fecha_inicio:
            fecha_texto = f"{fecha_inicio.strftime('%b %Y') if fecha_inicio else ''}"
            if fecha_fin:
                fecha_texto += f" - {fecha_fin.strftime('%b %Y')}"
            else:
                fecha_texto += " - Presente"
            items.append(Paragraph(fecha_texto, self.styles['DateStyle']))
        
        # Descripción
        if descripcion:
            items.append(Paragraph(descripcion, self.styles['Description']))
        
        items.append(Spacer(1, 0.12*inch))
        
        # Agregar todos los items como grupo
        self.story.extend(items)
    
    def _add_datos_personales(self):
        """Añade datos personales si son relevantes"""
        datos_relevantes = []
        
        if self.datos.fechanacimiento:
            edad = (datetime.now().date() - self.datos.fechanacimiento).days // 365
            datos_relevantes.append(f"<b>Edad:</b> {edad} años")
        
        if self.datos.estadocivil:
            datos_relevantes.append(f"<b>Estado Civil:</b> {self.datos.estadocivil}")
        
        if self.datos.cedula:
            datos_relevantes.append(f"<b>Cédula:</b> {self.datos.cedula}")
        
        if datos_relevantes:
            self._add_section_title("INFORMACIÓN PERSONAL", "👤")
            
            # Crear tabla de dos columnas para datos personales
            table_data = []
            for i in range(0, len(datos_relevantes), 2):
                row = [datos_relevantes[i]]
                if i + 1 < len(datos_relevantes):
                    row.append(datos_relevantes[i + 1])
                else:
                    row.append("")
                table_data.append(row)
            
            info_table = Table(table_data, colWidths=[3.25*inch, 3.25*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.DARK_TEXT),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            self.story.append(info_table)
            self.story.append(Spacer(1, 0.15*inch))
    
    def _add_experiencia_laboral(self):
        """Añade experiencia laboral con diseño moderno"""
        experiencias = self.datos.experiencias_laborales.filter(activo=True).order_by('-fecha_inicio')
        
        if not experiencias.exists():
            return
        
        self._add_section_title("EXPERIENCIA PROFESIONAL", "💼")
        
        for exp in experiencias:
            self._add_experience_item(
                cargo=exp.cargo,
                empresa=exp.empresa,
                fecha_inicio=exp.fecha_inicio,
                fecha_fin=exp.fecha_fin,
                descripcion=exp.descripcion
            )
    
    def _add_reconocimientos(self):
        """Añade reconocimientos y logros"""
        reconocimientos = self.datos.reconocimientos.filter(activo=True).order_by('-fecha')
        
        if not reconocimientos.exists():
            return
        
        self._add_section_title("RECONOCIMIENTOS Y LOGROS", "🏆")
        
        for rec in reconocimientos:
            items = []
            
            titulo = f"<b>{rec.nombrereconocimiento}</b>"
            if rec.otorgadopor:
                titulo += f" - {rec.otorgadopor}"
            
            items.append(Paragraph(titulo, self.styles['JobTitle']))
            
            if rec.fecha:
                items.append(Paragraph(
                    rec.fecha.strftime('%B %Y'),
                    self.styles['DateStyle']
                ))
            
            if rec.descripcion:
                items.append(Paragraph(rec.descripcion, self.styles['Description']))
            
            items.append(Spacer(1, 0.12*inch))
            self.story.extend(items)
    
    def _add_cursos(self):
        """Añade cursos y certificaciones"""
        cursos = self.datos.cursos_realizados.filter(activo=True).order_by('-fecha_inicio')
        
        if not cursos.exists():
            return
        
        self._add_section_title("FORMACIÓN Y CERTIFICACIONES", "📚")
        
        for curso in cursos:
            items = []
            
            # Nombre del curso
            items.append(Paragraph(f"<b>{curso.nombrecurso}</b>", self.styles['JobTitle']))
            
            # Institución
            if curso.institucion:
                items.append(Paragraph(curso.institucion, self.styles['Company']))
            
            # Fechas y horas
            fecha_info = []
            if curso.fecha_inicio:
                fecha_texto = curso.fecha_inicio.strftime('%b %Y')
                if curso.fecha_fin:
                    fecha_texto += f" - {curso.fecha_fin.strftime('%b %Y')}"
                fecha_info.append(fecha_texto)
            
            if curso.totalhoras:
                fecha_info.append(f"{curso.totalhoras} horas")
            
            if fecha_info:
                items.append(Paragraph(
                    " | ".join(fecha_info),
                    self.styles['DateStyle']
                ))
            
            # Descripción
            if curso.descripcioncurso:
                items.append(Paragraph(curso.descripcioncurso, self.styles['Description']))
            
            # Certificado
            if curso.certificado:
                cert_name = os.path.basename(curso.certificado.name)
                if cert_name.lower().endswith('.pdf'):
                    self.certificados_para_incrustar.append({
                        'file_field': curso.certificado,
                        'titulo': f"Certificado: {curso.nombrecurso}"
                    })
                    items.append(Paragraph(
                        f"📎 Certificado adjunto",
                        self.styles['Badge']
                    ))
            
            items.append(Spacer(1, 0.12*inch))
            self.story.extend(items)
    
    def _add_productos_academicos(self):
        """Añade productos académicos"""
        productos = self.datos.productos_academicos.filter(activo=True)
        
        if not productos.exists():
            return
        
        self._add_section_title("PRODUCCIÓN ACADÉMICA", "📖")
        
        for prod in productos:
            items = []
            
            titulo = f"<b>{prod.nombrerecurso}</b>"
            if prod.clasificador:
                titulo += f" ({prod.clasificador})"
            
            items.append(Paragraph(titulo, self.styles['JobTitle']))
            
            if prod.descripcion:
                items.append(Paragraph(prod.descripcion, self.styles['Description']))
            
            items.append(Spacer(1, 0.12*inch))
            self.story.extend(items)
    
    def _add_footer(self):
        """Añade pie de página profesional"""
        self.story.append(Spacer(1, 0.3*inch))
        
        fecha = datetime.now().strftime('%d de %B de %Y')
        footer_style = ParagraphStyle(
            'ModernFooter',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=self.LIGHT_TEXT,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        
        self.story.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=self.LIGHT_TEXT,
            spaceBefore=10,
            spaceAfter=10
        ))
        
        self.story.append(Paragraph(
            f"Curriculum Vitae generado el {fecha}",
            footer_style
        ))
    
    def generate(self):
        """Genera el PDF profesional"""
        try:
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.6*inch,
                bottomMargin=0.6*inch
            )
            
            # Construir documento
            self._add_modern_header()
            self._add_datos_personales()
            
            if self.datos.experiencias_laborales.filter(activo=True).exists():
                self._add_experiencia_laboral()
            
            if self.datos.reconocimientos.filter(activo=True).exists():
                self._add_reconocimientos()
            
            if self.datos.cursos_realizados.filter(activo=True).exists():
                self._add_cursos()
            
            if self.datos.productos_academicos.filter(activo=True).exists():
                self._add_productos_academicos()
            
            self._add_footer()
            
            # Construir PDF
            doc.build(self.story)
            
            # Incrustar certificados si existen
            if self.certificados_para_incrustar:
                pdf_buffer.seek(0)
                pdf_buffer = self._incrustar_certificados(pdf_buffer)
            
            # Limpiar archivos temporales
            self._cleanup_temp_files()
            
            pdf_buffer.seek(0)
            return pdf_buffer
        
        except Exception as e:
            print(f"Error generando PDF: {e}")
            self._cleanup_temp_files()
            return None
    
    def _incrustar_certificados(self, pdf_principal_buffer):
        """Incrusta certificados PDF al final"""
        try:
            pdf_reader = PdfReader(pdf_principal_buffer)
            writer = PdfWriter()
            
            for page_num in range(len(pdf_reader.pages)):
                writer.add_page(pdf_reader.pages[page_num])
            
            for cert_info in self.certificados_para_incrustar:
                cert_field = cert_info.get('file_field')
                
                if not cert_field:
                    continue
                
                try:
                    temp_path, content = self._download_file_from_storage(cert_field)
                    
                    if not temp_path or not content:
                        continue
                    
                    cert_buffer = BytesIO(content)
                    cert_buffer.seek(0)
                    cert_reader = PdfReader(cert_buffer)
                    
                    for page_num in range(len(cert_reader.pages)):
                        writer.add_page(cert_reader.pages[page_num])
                
                except Exception as e:
                    print(f"Error con certificado: {e}")
                    continue
            
            output_buffer = BytesIO()
            writer.write(output_buffer)
            
            return output_buffer
        
        except Exception as e:
            print(f"Error incrustando certificados: {e}")
            return pdf_principal_buffer
    
    def _cleanup_temp_files(self):
        """Limpia archivos temporales"""
        if hasattr(self, 'temp_files'):
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
