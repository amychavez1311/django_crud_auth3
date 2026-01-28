from django import forms
from django.core.exceptions import ValidationError
from datetime import date
import re
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
    # Country choices: (code, display)
    # Comprehensive list of country calling codes (prefix, display)
    COUNTRY_CHOICES = [
        ('+1', '+1 United States/Canada'),
        ('+7', '+7 Russia/Kazakhstan'),
        ('+20', '+20 Egypt'),
        ('+27', '+27 South Africa'),
        ('+30', '+30 Greece'),
        ('+31', '+31 Netherlands'),
        ('+32', '+32 Belgium'),
        ('+33', '+33 France'),
        ('+34', '+34 Spain'),
        ('+36', '+36 Hungary'),
        ('+39', '+39 Italy'),
        ('+40', '+40 Romania'),
        ('+41', '+41 Switzerland'),
        ('+43', '+43 Austria'),
        ('+44', '+44 United Kingdom'),
        ('+45', '+45 Denmark'),
        ('+46', '+46 Sweden'),
        ('+47', '+47 Norway'),
        ('+48', '+48 Poland'),
        ('+49', '+49 Germany'),
        ('+51', '+51 Peru'),
        ('+52', '+52 Mexico'),
        ('+53', '+53 Cuba'),
        ('+54', '+54 Argentina'),
        ('+55', '+55 Brazil'),
        ('+56', '+56 Chile'),
        ('+57', '+57 Colombia'),
        ('+58', '+58 Venezuela'),
        ('+60', '+60 Malaysia'),
        ('+61', '+61 Australia'),
        ('+62', '+62 Indonesia'),
        ('+63', '+63 Philippines'),
        ('+64', '+64 New Zealand'),
        ('+65', '+65 Singapore'),
        ('+66', '+66 Thailand'),
        ('+81', '+81 Japan'),
        ('+82', '+82 Korea (South)'),
        ('+84', '+84 Vietnam'),
        ('+86', '+86 China'),
        ('+90', '+90 Turkey'),
        ('+91', '+91 India'),
        ('+92', '+92 Pakistan'),
        ('+93', '+93 Afghanistan'),
        ('+94', '+94 Sri Lanka'),
        ('+95', '+95 Myanmar'),
        ('+98', '+98 Iran'),
        ('+211', '+211 South Sudan'),
        ('+212', '+212 Morocco'),
        ('+213', '+213 Algeria'),
        ('+216', '+216 Tunisia'),
        ('+218', '+218 Libya'),
        ('+220', '+220 Gambia'),
        ('+221', '+221 Senegal'),
        ('+222', '+222 Mauritania'),
        ('+223', '+223 Mali'),
        ('+224', '+224 Guinea'),
        ('+225', '+225 Cote d\'Ivoire'),
        ('+226', '+226 Burkina Faso'),
        ('+227', '+227 Niger'),
        ('+228', '+228 Togo'),
        ('+229', '+229 Benin'),
        ('+230', '+230 Mauritius'),
        ('+231', '+231 Liberia'),
        ('+232', '+232 Sierra Leone'),
        ('+233', '+233 Ghana'),
        ('+234', '+234 Nigeria'),
        ('+235', '+235 Chad'),
        ('+236', '+236 Central African Republic'),
        ('+237', '+237 Cameroon'),
        ('+238', '+238 Cape Verde'),
        ('+239', '+239 Sao Tome & Principe'),
        ('+240', '+240 Equatorial Guinea'),
        ('+241', '+241 Gabon'),
        ('+242', '+242 Republic of the Congo'),
        ('+243', '+243 DR Congo'),
        ('+244', '+244 Angola'),
        ('+245', '+245 Guinea-Bissau'),
        ('+246', '+246 British Indian Ocean Territory'),
        ('+248', '+248 Seychelles'),
        ('+249', '+249 Sudan'),
        ('+250', '+250 Rwanda'),
        ('+251', '+251 Ethiopia'),
        ('+252', '+252 Somalia'),
        ('+253', '+253 Djibouti'),
        ('+254', '+254 Kenya'),
        ('+255', '+255 Tanzania'),
        ('+256', '+256 Uganda'),
        ('+257', '+257 Burundi'),
        ('+258', '+258 Mozambique'),
        ('+260', '+260 Zambia'),
        ('+261', '+261 Madagascar'),
        ('+262', '+262 Reunion/Mayotte'),
        ('+263', '+263 Zimbabwe'),
        ('+264', '+264 Namibia'),
        ('+265', '+265 Malawi'),
        ('+266', '+266 Lesotho'),
        ('+267', '+267 Botswana'),
        ('+268', '+268 Eswatini'),
        ('+269', '+269 Comoros'),
        ('+290', '+290 Saint Helena'),
        ('+291', '+291 Eritrea'),
        ('+297', '+297 Aruba'),
        ('+298', '+298 Faroe Islands'),
        ('+299', '+299 Greenland'),
        ('+350', '+350 Gibraltar'),
        ('+351', '+351 Portugal'),
        ('+352', '+352 Luxembourg'),
        ('+353', '+353 Ireland'),
        ('+354', '+354 Iceland'),
        ('+355', '+355 Albania'),
        ('+356', '+356 Malta'),
        ('+357', '+357 Cyprus'),
        ('+358', '+358 Finland'),
        ('+359', '+359 Bulgaria'),
        ('+370', '+370 Lithuania'),
        ('+371', '+371 Latvia'),
        ('+372', '+372 Estonia'),
        ('+373', '+373 Moldova'),
        ('+374', '+374 Armenia'),
        ('+375', '+375 Belarus'),
        ('+376', '+376 Andorra'),
        ('+377', '+377 Monaco'),
        ('+378', '+378 San Marino'),
        ('+379', '+379 Vatican City'),
        ('+380', '+380 Ukraine'),
        ('+381', '+381 Serbia'),
        ('+382', '+382 Montenegro'),
        ('+383', '+383 Kosovo'),
        ('+385', '+385 Croatia'),
        ('+386', '+386 Slovenia'),
        ('+387', '+387 Bosnia & Herzegovina'),
        ('+389', '+389 North Macedonia'),
        ('+420', '+420 Czech Republic'),
        ('+421', '+421 Slovakia'),
        ('+423', '+423 Liechtenstein'),
        ('+500', '+500 Falkland Islands'),
        ('+501', '+501 Belize'),
        ('+502', '+502 Guatemala'),
        ('+503', '+503 El Salvador'),
        ('+504', '+504 Honduras'),
        ('+505', '+505 Nicaragua'),
        ('+506', '+506 Costa Rica'),
        ('+507', '+507 Panama'),
        ('+508', '+508 Saint Pierre & Miquelon'),
        ('+509', '+509 Haiti'),
        ('+590', '+590 Guadeloupe'),
        ('+591', '+591 Bolivia'),
        ('+592', '+592 Guyana'),
        ('+593', '+593 Ecuador'),
        ('+594', '+594 French Guiana'),
        ('+595', '+595 Paraguay'),
        ('+596', '+596 Martinique'),
        ('+597', '+597 Suriname'),
        ('+598', '+598 Uruguay'),
        ('+599', '+599 Caribbean Netherlands'),
        ('+670', '+670 Timor-Leste'),
        ('+671', '+671 Northern Mariana Islands'),
        ('+672', '+672 Australian External Territories'),
        ('+673', '+673 Brunei'),
        ('+674', '+674 Nauru'),
        ('+675', '+675 Papua New Guinea'),
        ('+676', '+676 Tonga'),
        ('+677', '+677 Solomon Islands'),
        ('+678', '+678 Vanuatu'),
        ('+679', '+679 Fiji'),
        ('+680', '+680 Palau'),
        ('+681', '+681 Wallis & Futuna'),
        ('+682', '+682 Cook Islands'),
        ('+683', '+683 Niue'),
        ('+685', '+685 Samoa'),
        ('+686', '+686 Kiribati'),
        ('+687', '+687 New Caledonia'),
        ('+688', '+688 Tuvalu'),
        ('+689', '+689 French Polynesia'),
        ('+690', '+690 Tokelau'),
        ('+691', '+691 Micronesia'),
        ('+692', '+692 Marshall Islands'),
        ('+850', '+850 North Korea'),
        ('+852', '+852 Hong Kong'),
        ('+853', '+853 Macau'),
        ('+855', '+855 Cambodia'),
        ('+856', '+856 Laos'),
        ('+880', '+880 Bangladesh'),
        ('+886', '+886 Taiwan'),
        ('+960', '+960 Maldives'),
        ('+961', '+961 Lebanon'),
        ('+962', '+962 Jordan'),
        ('+963', '+963 Syria'),
        ('+964', '+964 Iraq'),
        ('+965', '+965 Kuwait'),
        ('+966', '+966 Saudi Arabia'),
        ('+967', '+967 Yemen'),
        ('+968', '+968 Oman'),
        ('+970', '+970 Palestine'),
        ('+971', '+971 United Arab Emirates'),
        ('+972', '+972 Israel'),
        ('+973', '+973 Bahrain'),
        ('+974', '+974 Qatar'),
        ('+975', '+975 Bhutan'),
        ('+976', '+976 Mongolia'),
        ('+977', '+977 Nepal'),
        ('+994', '+994 Azerbaijan'),
        ('+995', '+995 Georgia'),
        ('+996', '+996 Kyrgyzstan'),
        ('+998', '+998 Uzbekistan'),
    ]

    class PhoneMultiWidget(forms.MultiWidget):
        def __init__(self, attrs=None, choices=None):
            if choices is None:
                choices = DatosPersonalesForm.COUNTRY_CHOICES
            widgets = [
                 forms.Select(choices=choices, attrs={'class': 'form-select', 'style': 'width:110px; display:inline-block; margin-right:8px;'}),
                 forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número', 'maxlength': '12', 'style': 'display:inline-block; width:calc(100% - 128px);'})
            ]
            super().__init__(widgets, attrs)

        def decompress(self, value):
            if not value:
                return [None, None]
            # If value contains a space, split country and number
            if ' ' in value:
                parts = value.split(' ', 1)
                return [parts[0], parts[1]]
            # Try to match known country codes (longest first)
            codes = sorted([c for c, _ in DatosPersonalesForm.COUNTRY_CHOICES], key=lambda x: -len(x))
            for code in codes:
                if value.startswith(code):
                    return [code, value[len(code):]]
            # fallback
            return [None, value]

    class PhoneMultiValueField(forms.MultiValueField):
        def __init__(self, *args, **kwargs):
            choices = kwargs.pop('choices', DatosPersonalesForm.COUNTRY_CHOICES)
            fields = [
                forms.ChoiceField(choices=choices),
                forms.CharField()
            ]
            super().__init__(fields=fields, require_all_fields=False, *args, **kwargs)

        def compress(self, data_list):
            if not data_list:
                return ''
            country = data_list[0] or ''
            number = data_list[1] or ''
            # Strip non digits from number
            number_digits = re.sub(r"\D", "", number)
            return f"{country} {number_digits}".strip()

        def clean(self, value):
            cleaned = super().clean(value)
            country = cleaned[0] if cleaned else ''
            number = cleaned[1] if cleaned else ''
            number_digits = re.sub(r"\D", "", number or "")
            if number_digits:
                if len(number_digits) > 12:
                    raise ValidationError('El número no puede tener más de 12 dígitos.')
            return self.compress([country, number_digits])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set max attribute on date inputs so UI cannot select future dates
        if 'fechanacimiento' in self.fields:
            self.fields['fechanacimiento'].widget.attrs.setdefault('max', date.today().isoformat())
        # Replace telefonoconvencional with a multi-field (country + number)
        if 'telefonoconvencional' in self.fields:
            self.fields['telefonoconvencional'] = DatosPersonalesForm.PhoneMultiValueField(
                widget=DatosPersonalesForm.PhoneMultiWidget(choices=DatosPersonalesForm.COUNTRY_CHOICES),
                required=False,
                label='Teléfono Convencional',
            )

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
            # telefonoconvencional uses a custom multiwidget defined in the form
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
        if fechanacimiento and fechanacimiento > date.today():
            raise ValidationError('La fecha de nacimiento no puede ser posterior al día de hoy.')
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
            'entidadpatrocinadora', 'nombrecontactoauspicia', 'telefonocontactoauspicia',
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

