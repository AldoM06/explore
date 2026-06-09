from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Booking, Tour

LANGUAGE_CHOICES = [
    ('Español', 'Español'),
    ('English', 'English'),
    ('Français', 'Français'),
    ('Italiano', 'Italiano'),
    ('中文 (Mandarín)', '中文 (Mandarín)'),
    ('Português', 'Português'),
]


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario o correo',
        widget=forms.TextInput(attrs={'placeholder': 'tu@correo.com o usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )


class ClientRegisterForm(UserCreationForm):
    first_name  = forms.CharField(label='Nombre', max_length=60,
                                  widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'}))
    last_name   = forms.CharField(label='Apellido', max_length=60,
                                  widget=forms.TextInput(attrs={'placeholder': 'Tu apellido'}))
    email       = forms.EmailField(label='Correo electrónico',
                                   widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}))
    phone       = forms.CharField(label='Teléfono', max_length=20, required=False,
                                  widget=forms.TextInput(attrs={'placeholder': '+52 55 0000 0000'}))
    nationality = forms.CharField(label='Nacionalidad', max_length=60, required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'México'}))
    language    = forms.ChoiceField(label='Idioma preferido', choices=LANGUAGE_CHOICES)
    password1   = forms.CharField(label='Contraseña',
                                  widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres'}))
    password2   = forms.CharField(label='Confirmar contraseña',
                                  widget=forms.PasswordInput(attrs={'placeholder': 'Repite tu contraseña'}))

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username   = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.email      = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role='client',
                phone=self.cleaned_data.get('phone', ''),
                nationality=self.cleaned_data.get('nationality', ''),
                language=self.cleaned_data.get('language', 'Español'),
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name  = forms.CharField(label='Nombre', max_length=60)
    last_name   = forms.CharField(label='Apellido', max_length=60)
    email       = forms.EmailField(label='Correo electrónico')

    class Meta:
        model  = UserProfile
        fields = ('phone', 'nationality', 'language')
        labels = {'phone': 'Teléfono', 'nationality': 'Nacionalidad', 'language': 'Idioma preferido'}
        widgets = {'language': forms.Select(choices=LANGUAGE_CHOICES)}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial  = self.user.last_name
            self.fields['email'].initial      = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name  = self.cleaned_data['last_name']
            self.user.email      = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class BookingRequestForm(forms.ModelForm):
    tour     = forms.ModelChoiceField(
        queryset=Tour.objects.filter(is_active=True),
        label='Tour de interés',
        empty_label='Selecciona un tour',
    )
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, label='Idioma del tour')

    class Meta:
        model  = Booking
        fields = ('tour', 'travel_date', 'num_people', 'language', 'notes')
        labels = {
            'travel_date': 'Fecha deseada',
            'num_people':  'Número de personas (máx. 10)',
            'notes':       'Peticiones especiales',
        }
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date'}),
            'num_people':  forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'notes':       forms.Textarea(attrs={'rows': 3, 'placeholder': 'Alergias, necesidades especiales, idioma, etc.'}),
        }


# ── ADMIN FORMS ────────────────────────────────────────────────

class AdminBookingForm(forms.ModelForm):
    """Formulario completo para el admin al crear/editar una reservación"""
    class Meta:
        model  = Booking
        fields = ('client', 'tour', 'tour_name', 'travel_date', 'num_people',
                  'language', 'status', 'total_price', 'notes', 'admin_notes')
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date'}),
            'notes':       forms.Textarea(attrs={'rows': 2}),
            'admin_notes': forms.Textarea(attrs={'rows': 2}),
        }


class AdminClientForm(forms.ModelForm):
    """Crear/editar cliente desde el panel admin"""
    first_name  = forms.CharField(label='Nombre')
    last_name   = forms.CharField(label='Apellido')
    email       = forms.EmailField(label='Correo / usuario')
    password    = forms.CharField(label='Contraseña', required=False,
                                  widget=forms.PasswordInput(),
                                  help_text='Déjalo vacío para no cambiarla.')

    class Meta:
        model  = UserProfile
        fields = ('role', 'phone', 'nationality', 'language', 'notes')

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if self.user_instance:
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial  = self.user_instance.last_name
            self.fields['email'].initial      = self.user_instance.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user_instance:
            self.user_instance.first_name = self.cleaned_data['first_name']
            self.user_instance.last_name  = self.cleaned_data['last_name']
            self.user_instance.email      = self.cleaned_data['email']
            pw = self.cleaned_data.get('password')
            if pw:
                self.user_instance.set_password(pw)
            if commit:
                self.user_instance.save()
        if commit:
            profile.save()
        return profile
