from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from functools import wraps

from .models import UserProfile, Booking, Tour, Document
from .forms import (LoginForm, ClientRegisterForm, ProfileUpdateForm,
                    BookingRequestForm, AdminBookingForm, AdminClientForm)
from core.models import ContactMessage


# ── DECORATORS ────────────────────────────────────────────────

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        try:
            if not request.user.profile.is_admin:
                messages.error(request, 'No tienes permiso para acceder a esa sección.')
                return redirect('accounts:client_dashboard')
        except UserProfile.DoesNotExist:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def client_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── AUTH ──────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'¡Bienvenido, {user.first_name or user.username}!')
        return _redirect_by_role(user)

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    form = ClientRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, '¡Cuenta creada! Bienvenido a Xplore.')
        return redirect('accounts:client_dashboard')

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def _redirect_by_role(user):
    try:
        if user.profile.is_admin:
            return redirect('accounts:admin_dashboard')
    except UserProfile.DoesNotExist:
        pass
    return redirect('accounts:client_dashboard')


# ── CLIENT PORTAL ─────────────────────────────────────────────

@client_required
def client_dashboard(request):
    bookings = Booking.objects.filter(client=request.user).select_related('tour')
    upcoming = bookings.filter(
        travel_date__gte=timezone.now().date(),
        status__in=['pending', 'confirmed']
    )
    past = bookings.filter(
        Q(travel_date__lt=timezone.now().date()) | Q(status='completed')
    )
    return render(request, 'accounts/client_dashboard.html', {
        'bookings': bookings,
        'upcoming': upcoming,
        'past':     past,
    })


@client_required
def client_booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    documents = booking.documents.all()
    return render(request, 'accounts/booking_detail.html', {
        'booking': booking, 'documents': documents
    })


@client_required
def client_new_booking(request):
    form = BookingRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.client    = request.user
        booking.tour_name = booking.tour.name if booking.tour else 'Tour personalizado'
        booking.save()
        messages.success(request, '¡Solicitud de reserva enviada! Te contactaremos pronto para confirmar.')
        return redirect('accounts:client_dashboard')
    return render(request, 'accounts/new_booking.html', {'form': form})


@client_required
def client_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'client'})
    form = ProfileUpdateForm(request.POST or None, instance=profile, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('accounts:client_profile')
    return render(request, 'accounts/client_profile.html', {'form': form, 'profile': profile})


# ── ADMIN PANEL ───────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    # Stats
    total_clients   = User.objects.filter(profile__role='client').count()
    total_bookings  = Booking.objects.count()
    confirmed       = Booking.objects.filter(status='confirmed').count()
    completed       = Booking.objects.filter(status='completed').count()
    pending         = Booking.objects.filter(status='pending').count()
    revenue         = Booking.objects.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Recent activity
    recent_bookings = Booking.objects.select_related('client', 'tour').order_by('-created_at')[:8]
    recent_contacts = ContactMessage.objects.order_by('-creado_en')[:5]

    # Popular tours
    popular_tours = Tour.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]

    # Monthly bookings (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_end   = (month_start + timedelta(days=32)).replace(day=1)
        count = Booking.objects.filter(
            created_at__gte=month_start, created_at__lt=month_end
        ).count()
        monthly_data.append({'month': month_start.strftime('%b'), 'count': count})

    return render(request, 'accounts/admin_dashboard.html', {
        'total_clients':  total_clients,
        'total_bookings': total_bookings,
        'confirmed':      confirmed,
        'completed':      completed,
        'pending':        pending,
        'revenue':        revenue,
        'recent_bookings':recent_bookings,
        'recent_contacts':recent_contacts,
        'popular_tours':  popular_tours,
        'monthly_data':   monthly_data,
    })


@admin_required
def admin_clients(request):
    q = request.GET.get('q', '')
    clients = User.objects.filter(profile__role='client').select_related('profile')
    if q:
        clients = clients.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    return render(request, 'accounts/admin_clients.html', {'clients': clients, 'q': q})


@admin_required
def admin_client_detail(request, pk):
    client  = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=client, defaults={'role': 'client'})
    bookings = Booking.objects.filter(client=client).select_related('tour')

    form = AdminClientForm(request.POST or None, instance=profile, user_instance=client)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cliente actualizado.')
        return redirect('accounts:admin_client_detail', pk=pk)

    return render(request, 'accounts/admin_client_detail.html', {
        'client': client, 'profile': profile,
        'bookings': bookings, 'form': form,
    })


@admin_required
def admin_create_client(request):
    """Admin crea manualmente un cliente"""
    from django.contrib.auth.forms import UserCreationForm
    form = ClientRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Cliente {user.get_full_name()} creado exitosamente.')
        return redirect('accounts:admin_client_detail', pk=user.pk)
    return render(request, 'accounts/admin_create_client.html', {'form': form})


@admin_required
def admin_bookings(request):
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')
    bookings = Booking.objects.select_related('client', 'tour').order_by('-created_at')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if q:
        bookings = bookings.filter(
            Q(client__first_name__icontains=q) | Q(client__last_name__icontains=q) |
            Q(tour_name__icontains=q)
        )
    from .models import STATUS_CHOICES
    return render(request, 'accounts/admin_bookings.html', {
        'bookings': bookings, 'status_filter': status_filter,
        'q': q, 'status_choices': STATUS_CHOICES,
    })


@admin_required
def admin_booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    documents = booking.documents.all()
    form = AdminBookingForm(request.POST or None, instance=booking)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reservación actualizada.')
        return redirect('accounts:admin_booking_detail', pk=pk)
    return render(request, 'accounts/admin_booking_detail.html', {
        'booking': booking, 'documents': documents, 'form': form,
    })


@admin_required
def admin_new_booking(request):
    form = AdminBookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reservación creada correctamente.')
        return redirect('accounts:admin_bookings')
    return render(request, 'accounts/admin_new_booking.html', {'form': form})


@admin_required
def admin_upload_document(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk)
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type', 'voucher')
        title    = request.POST.get('title', 'Documento')
        file     = request.FILES.get('file')
        if file:
            Document.objects.create(booking=booking, doc_type=doc_type, title=title, file=file)
            messages.success(request, 'Documento subido correctamente.')
        return redirect('accounts:admin_booking_detail', pk=booking_pk)
    return redirect('accounts:admin_booking_detail', pk=booking_pk)


@admin_required
def admin_contacts(request):
    contacts = ContactMessage.objects.order_by('-creado_en')
    return render(request, 'accounts/admin_contacts.html', {'contacts': contacts})
