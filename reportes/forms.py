"""
Módulo de Formularios para la aplicación de Reportes.
Contiene los ModelForm personalizados utilizados para validar y procesar
la entrada de datos de reportes ciudadanos en el sistema.
"""

from django import forms
from .models import Reporte, Categoria


class MultipleFileInput(forms.FileInput):
    """
    Widget personalizado que permite la selección múltiple de archivos de imagen
    sin generar excepciones en el validador estricto por defecto de Django.
    """
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class ReporteForm(forms.ModelForm):
    """
    Formulario para la creación y edición de Reportes por parte de los ciudadanos.
    Utiliza widgets ocultos para capturar datos geográficos (coordenadas y dirección)
    seleccionados interactivamente a través del mapa en el frontend.
    """
    class Meta:
        model = Reporte

        # Campos expuestos en el formulario
        fields = [
            'categoria',
            'descripcion',
            'latitud',
            'longitud',
            'calle',
            'colonia',
            'codigo_postal',
            'referencia',
            'foto',
        ]

        # Configuración de estilos y widgets de los campos
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),

            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el incidente si deseas agregar más detalles...'
            }),

            # Campos geográficos ocultos/visibles que se rellenan mediante la API del mapa
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
            'calle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Av. Costera Miguel Alemán 123',
                'id': 'id_calle'
            }),
            'colonia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Fracc. Hornos',
                'id': 'id_colonia'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 39670',
                'id': 'id_codigo_postal'
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Frente a la tienda OXXO o entre calle A y B',
                'id': 'id_referencia'
            }),

            'foto': MultipleFileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg, .jpeg, image/jpeg',
                'id': 'id_foto',
                'multiple': True
            }),
        }

        # Etiquetas personalizadas legibles para el usuario
        labels = {
            'categoria': 'Tipo de incidente',
            'descripcion': 'Descripción opcional',
            'referencia': 'Referencias de la ubicación (opcional)',
            'foto': 'Evidencia fotográfica (1 a 3 fotos en formato JPG)',
        }

    def __init__(self, *args, **kwargs):
        """
        Constructor del formulario. Carga todas las categorías disponibles en la base de datos.
        """
        super().__init__(*args, **kwargs)

        # Cargar todas las categorías disponibles en la base de datos
        self.fields['categoria'].queryset = Categoria.objects.all()

        # Hacer que descripción y referencia sean opcionales. Las fotos se validan en la vista (1 a 3 fotos JPG).
        self.fields['descripcion'].required = False
        self.fields['referencia'].required = False
        self.fields['foto'].required = False

    def clean(self):
        """
        Validación general del formulario. Exige que el usuario haya marcado
        una ubicación en el mapa interactivo (comprobando latitud y longitud).
        """
        cleaned_data = super().clean()

        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')

        if not latitud or not longitud:
            raise forms.ValidationError('Debes seleccionar la ubicación en el mapa.')

        return cleaned_data