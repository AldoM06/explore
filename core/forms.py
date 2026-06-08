from django import forms
from .models import ContactMessage

TOURS = [
    ('', 'Selecciona un tour (opcional)'),
    ('teotihuacan', 'Teotihuacán – Ciudad de los Dioses'),
    ('chichen-itza', 'Chichén Itzá – Maravilla del Mundo'),
    ('monte-alban', 'Monte Albán – Capital Zapoteca'),
    ('palenque', 'Palenque – Joya de la Selva'),
    ('tulum', 'Tulum – Fortaleza Maya'),
    ('uxmal', 'Uxmal – Ciudad de los Templos'),
]

from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    # 🔹 Agregar el campo tour con las opciones
    tour = forms.ChoiceField(
        choices=TOURS,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = ContactMessage
        fields = ['nombre', 'email', 'telefono', 'tour', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tucorreo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52 55 1234 5678'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '¿Cómo podemos ayudarte?',
                'rows': 4
            }),
        }