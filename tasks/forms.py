from django import forms
from datetime import date, timedelta
from .models import (
    Task, DatosPersonales, ExperienciaLaboral, Reconocimiento,
    CursoRealizado, ProductoAcademico, ProductoLaboral, VentaGarage
)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder':'Write a title'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'placeholder':'Write a description'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }


# ============================
# FORMULARIOS PARA HOJA DE VIDA
# ============================

class DatosPersonalesForm(forms.ModelForm):
    """Formulario para datos personales"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # asegurar que el date input solo permita fechas anteriores a hoy
        try:
            yesterday = date.today() - timedelta(days=1)
            if 'fechanacimiento' in self.fields:
                self.fields['fechanacimiento'].widget.attrs['max'] = yesterday.isoformat()
        except Exception:
            pass
    
    class Meta:
        model = DatosPersonales
        fields = [
            'apellidos', 'nombres', 'nacionalidad', 'lugarnacimiento',
            'fechanacimiento', 'numerocedula', 'sexo', 'estadocivil',
            'licenciaconducir', 'telefonoconvencional', 'telefonofijo',
            'direcciondomiciliaria', 'direcciontrabajo', 'sitioweb',
            'descripcionperfil', 'fotoperfil', 'perfilactivo'
        ]
        widgets = {
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos',
                'required': 'required'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres',
                'required': 'required'
            }),
            'nacionalidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nacionalidad'
            }),
            'lugarnacimiento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar de Nacimiento'
            }),
            'fechanacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numerocedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de Cédula',
                'required': 'required'
            }),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'estadocivil': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado Civil'
            }),
            'licenciaconducir': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Licencia de Conducir'
            }),
            'telefonoconvencional': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono Convencional'
            }),
            'telefonofijo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono Fijo'
            }),
            'direcciondomiciliaria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección Domiciliaria'
            }),
            'direcciontrabajo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección de Trabajo'
            }),
            'sitioweb': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sitio Web'
            }),
            'descripcionperfil': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del Perfil',
                'rows': 3
            }),
            'fotoperfil': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'perfilactivo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_fechanacimiento(self):
        fechanacimiento = self.cleaned_data.get('fechanacimiento')
        if fechanacimiento:
            if fechanacimiento >= date.today():
                raise forms.ValidationError('La fecha de nacimiento debe ser anterior a hoy.')
        return fechanacimiento


class ExperienciaLaboralForm(forms.ModelForm):
    """Formulario para experiencia laboral"""
    
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'cargodesempenado', 'nombreempresa', 'lugarempresa',
            'emailempresa', 'sitiowebempresa', 'nombrecontactoempresarial',
            'telefonocontactoempresarial', 'fechainiciogestion', 'fechafingestion',
            'descripcionfunciones', 'certificado', 'activo'
        ]
        widgets = {
            'cargodesempenado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo Desempeñado',
                'required': 'required'
            }),
            'nombreempresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la Empresa',
                'required': 'required'
            }),
            'lugarempresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar de la Empresa'
            }),
            'emailempresa': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email de la Empresa'
            }),
            'sitiowebempresa': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sitio Web de la Empresa'
            }),
            'nombrecontactoempresarial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de Contacto'
            }),
            'telefonocontactoempresarial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de Contacto'
            }),
            'fechainiciogestion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'fechafingestion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'descripcionfunciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de Funciones',
                'rows': 3
            }),
            'certificado': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ReconocimientoForm(forms.ModelForm):
    """Formulario para reconocimientos"""
    
    class Meta:
        model = Reconocimiento
        fields = [
            'tiporeconocimiento', 'fechareconocimiento', 'descripcionreconocimiento',
            'entidad patrocinadora', 'nombrecontactoauspicia', 'telefonocontactoauspicia',
            'certificado', 'activo'
        ]
        widgets = {
            'tiporeconocimiento': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'fechareconocimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'descripcionreconocimiento': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del Reconocimiento',
                'rows': 3
            }),
            'entidad patrocinadora': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entidad Patrocinadora',
                'required': 'required'
            }),
            'nombrecontactoauspicia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Contacto'
            }),
            'telefonocontactoauspicia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del Contacto'
            }),
            'certificado': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class CursoRealizadoForm(forms.ModelForm):
    """Formulario para cursos realizados"""
    
    class Meta:
        model = CursoRealizado
        fields = [
            'nombrecurso', 'fechainicio', 'fechafin', 'totalhoras',
            'descripcioncurso', 'entidadpatrocinadora', 'nombrecontactoauspicia',
            'telefonocontactoauspicia', 'emailempresapatrocinadora',
            'certificado', 'activo'
        ]
        widgets = {
            'nombrecurso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Curso',
                'required': 'required'
            }),
            'fechainicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'fechafin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'totalhoras': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total de Horas'
            }),
            'descripcioncurso': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del Curso',
                'rows': 3
            }),
            'entidadpatrocinadora': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entidad Patrocinadora',
                'required': 'required'
            }),
            'nombrecontactoauspicia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Contacto'
            }),
            'telefonocontactoauspicia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del Contacto'
            }),
            'emailempresapatrocinadora': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email de la Entidad'
            }),
            'certificado': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ProductoAcademicoForm(forms.ModelForm):
    """Formulario para productos académicos"""
    
    class Meta:
        model = ProductoAcademico
        fields = ['nombrerecurso', 'clasificador', 'descripcion', 'activo']
        widgets = {
            'nombrerecurso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Recurso',
                'required': 'required'
            }),
            'clasificador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clasificador',
                'required': 'required'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción',
                'rows': 3
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ProductoLaboralForm(forms.ModelForm):
    """Formulario para productos laborales"""
    
    class Meta:
        model = ProductoLaboral
        fields = ['nombreproducto', 'fechaproducto', 'descripcion', 'activo']
        widgets = {
            'nombreproducto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Producto',
                'required': 'required'
            }),
            'fechaproducto': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción',
                'rows': 3
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class VentaGarageForm(forms.ModelForm):
    """Formulario para ventas garage"""
    
    class Meta:
        model = VentaGarage
        fields = ['nombreproducto', 'estadoproducto', 'descripcion', 'valordelbien', 'activo']
        widgets = {
            'nombreproducto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Producto',
                'required': 'required'
            }),
            'estadoproducto': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción',
                'rows': 3
            }),
            'valordelbien': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor del Bien',
                'step': '0.01',
                'required': 'required'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

