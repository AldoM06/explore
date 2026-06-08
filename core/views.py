from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from .telegram_notify import send_telegram_notification


def home(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            send_telegram_notification(contact)
            messages.success(request, '¡Gracias! Nos pondremos en contacto contigo muy pronto.')
            return redirect('home')
        else:
            messages.error(request, 'Por favor revisa los campos del formulario.')

    return render(request, 'core/home.html', {'form': form})
