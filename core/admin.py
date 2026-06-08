from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'email', 'telefono', 'tour', 'creado_en')
    list_filter   = ('tour', 'creado_en')
    search_fields = ('nombre', 'email', 'mensaje')
    readonly_fields = ('creado_en',)
