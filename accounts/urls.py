from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/',    views.login_view,    name='login'),
    path('registro/', views.register_view, name='register'),
    path('salir/',    views.logout_view,   name='logout'),

    # Client portal
    path('mi-cuenta/',                         views.client_dashboard,       name='client_dashboard'),
    path('mi-cuenta/reservas/<int:pk>/',       views.client_booking_detail,  name='client_booking_detail'),
    path('mi-cuenta/nueva-reserva/',           views.client_new_booking,     name='client_new_booking'),
    path('mi-cuenta/perfil/',                  views.client_profile,         name='client_profile'),

    # Admin panel
    path('admin-xplore/',                             views.admin_dashboard,        name='admin_dashboard'),
    path('admin-xplore/clientes/',                    views.admin_clients,          name='admin_clients'),
    path('admin-xplore/clientes/nuevo/',              views.admin_create_client,    name='admin_create_client'),
    path('admin-xplore/clientes/<int:pk>/',           views.admin_client_detail,    name='admin_client_detail'),
    path('admin-xplore/reservaciones/',               views.admin_bookings,         name='admin_bookings'),
    path('admin-xplore/reservaciones/nueva/',         views.admin_new_booking,      name='admin_new_booking'),
    path('admin-xplore/reservaciones/<int:pk>/',      views.admin_booking_detail,   name='admin_booking_detail'),
    path('admin-xplore/reservaciones/<int:booking_pk>/subir/', views.admin_upload_document, name='admin_upload_document'),
    path('admin-xplore/contactos/',                   views.admin_contacts,         name='admin_contacts'),
]
