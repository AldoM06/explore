import requests
import os
import urllib.parse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def send_telegram_notification(contact):
    """
    Envía un mensaje a Telegram cuando llega un nuevo contacto.
    Incluye un botón para abrir WhatsApp directamente con el cliente.
    """
    # Obtener variables de entorno
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # Verificar configuración
    if TELEGRAM_BOT_TOKEN == 'TU_TOKEN_AQUI' or TELEGRAM_CHAT_ID == 'TU_CHAT_ID_AQUI':
        print("[Telegram] ⚠️ Configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en el archivo .env")
        return False

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] ⚠️ Faltan variables de entorno")
        return False

    # Preparar texto del mensaje
    tour_texto = contact.tour if hasattr(contact, 'tour') and contact.tour else "No especificado"
    tel_texto = contact.telefono if hasattr(contact, 'telefono') and contact.telefono else "No proporcionado"

    mensaje = (
        "🏛️ *Nuevo contacto en Xplore*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Nombre:*   {contact.nombre}\n"
        f"📧 *Email:*    {contact.email}\n"
        f"📞 *Teléfono:* {tel_texto}\n"
        f"🗺️ *Tour:*     {tour_texto}\n"
        f"💬 *Mensaje:*\n_{contact.mensaje}_\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {contact.creado_en.strftime('%d/%m/%Y %H:%M')} (CDMX)"
    )

    # ✅ Crear botón de WhatsApp si hay teléfono
    inline_keyboard = []
    if contact.telefono and contact.telefono != "No proporcionado":
        # Limpiar el teléfono (quitar espacios, guiones, etc.)
        telefono_limpio = ''.join(filter(str.isdigit, contact.telefono))
        
        # Si el teléfono tiene menos de 10 dígitos, agregar código de México (+52)
        if len(telefono_limpio) < 10:
            telefono_limpio = "52" + telefono_limpio
        
        # ✅ Mensaje pre-escrito con emojis y espacios (se codificará automáticamente)
        mensaje_wa = f"👋 ¡Hola {contact.nombre}! 👋\n\nVi tu mensaje en Xplore. ¿Cómo podemos ayudarte?"
        mensaje_codificado = urllib.parse.quote(mensaje_wa)
        
        # Crear el botón de WhatsApp con el mensaje codificado
        wa_link = f"https://wa.me/{telefono_limpio}?text={mensaje_codificado}"
        inline_keyboard = [
            [{"text": "💬 Hablar por WhatsApp", "url": wa_link}]
        ]

    # Construir el payload con el botón
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': mensaje,
        'parse_mode': 'Markdown',
    }
    
    if inline_keyboard:
        payload['reply_markup'] = {
            'inline_keyboard': inline_keyboard
        }

    # ✅ Enviar mensaje a Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("[Telegram] ✅ Notificación enviada correctamente con botón de WhatsApp")
        return True
    except Exception as e:
        print(f"[Telegram] ❌ Error al enviar notificación: {e}")
        return False