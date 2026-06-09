from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Perfil extendido para clientes"""
    ROLE_CHOICES = [('client', 'Cliente'), ('admin', 'Administrador')]

    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    phone       = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    nationality = models.CharField(max_length=60, blank=True, verbose_name='Nacionalidad')
    language    = models.CharField(max_length=30, blank=True, verbose_name='Idioma preferido')
    notes       = models.TextField(blank=True, verbose_name='Notas internas (solo admin)')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuarios'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff


class Tour(models.Model):
    """Catálogo de tours disponibles"""
    name        = models.CharField(max_length=120, verbose_name='Nombre del tour')
    location    = models.CharField(max_length=100, verbose_name='Ubicación')
    duration    = models.CharField(max_length=50, verbose_name='Duración', help_text='Ej: 90 minutos, 2 días')
    description = models.TextField(verbose_name='Descripción')
    price       = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio base (MXN)')
    is_active   = models.BooleanField(default=True, verbose_name='Activo')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tour'
        verbose_name_plural = 'Tours'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.location}"


STATUS_CHOICES = [
    ('pending',   'Pendiente de confirmación'),
    ('confirmed', 'Confirmado'),
    ('completed', 'Completado'),
    ('cancelled', 'Cancelado'),
]


class Booking(models.Model):
    """Reservación / viaje de un cliente"""
    client       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name='Cliente')
    tour         = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, related_name='bookings', verbose_name='Tour')
    tour_name    = models.CharField(max_length=120, verbose_name='Nombre del tour', help_text='Se guarda por si se elimina el tour')
    travel_date  = models.DateField(verbose_name='Fecha del viaje')
    num_people   = models.PositiveIntegerField(default=1, verbose_name='Número de personas')
    language     = models.CharField(max_length=30, default='Español', verbose_name='Idioma del tour')
    status       = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    total_price  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Precio total (MXN)')
    notes        = models.TextField(blank=True, verbose_name='Notas / peticiones especiales')
    admin_notes  = models.TextField(blank=True, verbose_name='Notas internas admin')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'
        ordering = ['-travel_date']

    def __str__(self):
        return f"{self.client.get_full_name() or self.client.username} · {self.tour_name} · {self.travel_date}"

    def save(self, *args, **kwargs):
        if self.tour and not self.tour_name:
            self.tour_name = self.tour.name
        super().save(*args, **kwargs)

    @property
    def status_color(self):
        return {
            'pending':   'amber',
            'confirmed': 'blue',
            'completed': 'green',
            'cancelled': 'red',
        }.get(self.status, 'gray')


class Document(models.Model):
    """Documentos adjuntos a una reservación (voucher, factura, etc.)"""
    DOC_TYPES = [
        ('voucher',  'Voucher de reservación'),
        ('invoice',  'Factura'),
        ('itinerary','Itinerario'),
        ('other',    'Otro'),
    ]

    booking   = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='documents', verbose_name='Reservación')
    doc_type  = models.CharField(max_length=12, choices=DOC_TYPES, default='voucher', verbose_name='Tipo de documento')
    title     = models.CharField(max_length=120, verbose_name='Título')
    file      = models.FileField(upload_to='documents/%Y/%m/', verbose_name='Archivo')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f"{self.get_doc_type_display()} — {self.booking}"
