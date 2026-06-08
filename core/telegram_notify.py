import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def send_telegram_notification(contact):
    """
    Envía un mensaje a Telegram cuando llega un nuevo contacto.
    """
    # Obtener variables de entorno
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # ✅ CORRECCIÓN 1: Verificar que estén configuradas
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

    # ✅ CORRECCIÓN 2 y 3: Usar las variables correctas
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    try:
        resp = requests.post(
            url,
            json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': mensaje,
                'parse_mode': 'Markdown',
            },
            timeout=10
        )
        resp.raise_for_status()
        print("[Telegram] ✅ Notificación enviada correctamente")
        return True
    except Exception as e:
        print(f"[Telegram] ❌ Error al enviar notificación: {e}")
        return False