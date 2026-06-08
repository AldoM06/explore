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

class ContactForm(forms.ModelForm):
    tour = forms.ChoiceField(choices=TOURS, required=False, label='Tour de interés')

    class Meta:
        model  = ContactMessage
        fields = ['nombre', 'email', 'telefono', 'tour', 'mensaje']
        labels = {
            'nombre':   'Nombre completo',
            'email':    'Correo electrónico',
            'telefono': 'Teléfono (opcional)',
            'mensaje':  'Mensaje',
        }
        widgets = {
            'nombre':   forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
            'email':    forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+52 55 0000 0000'}),
            'mensaje':  forms.Textarea(attrs={'placeholder': '¿En qué podemos ayudarte?', 'rows': 4}),
        }
