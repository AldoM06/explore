# 🏛️ Terra Antigua — Sitio Web Django

Sitio web responsivo para empresa de turismo arqueológico con formulario de contacto
que envía notificaciones automáticas a Telegram.

---

## 🚀 Instalación rápida

```bash
# 1. Clona o descarga el proyecto
cd terra_antigua

# 2. Crea entorno virtual
python -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Configura variables de entorno (ver sección Telegram abajo)

# 5. Aplica migraciones
python manage.py migrate

# 6. Crea superusuario para el admin
python manage.py createsuperuser

# 7. Corre el servidor
python manage.py runserver
```

Abre http://127.0.0.1:8000 en tu navegador.

---

## 📱 Configurar Bot de Telegram

### Paso 1 — Crear el Bot

1. Abre Telegram y busca **@BotFather**
2. Escribe `/newbot`
3. Ponle un nombre, p.ej. `Terra Antigua Notificaciones`
4. Copia el **TOKEN** que te da (se ve así: `7012345678:AAH...`)

### Paso 2 — Obtener tu Chat ID

**Opción A (canal privado):**
1. Crea un grupo en Telegram y agrega tu bot como admin
2. Manda cualquier mensaje al grupo
3. Visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
4. Copia el valor de `"id"` dentro de `"chat"` (puede ser negativo, ej: `-1001234567890`)

**Opción B (mensaje directo al bot):**
1. Escríbele un mensaje a tu bot
2. Visita la URL de getUpdates
3. Copia el `id` de tu chat personal (número positivo)

### Paso 3 — Configurar credenciales

**Opción recomendada: Variables de entorno**

```bash
# Mac/Linux
export TELEGRAM_BOT_TOKEN="7012345678:AAH..."
export TELEGRAM_CHAT_ID="-1001234567890"
python manage.py runserver

# Windows (CMD)
set TELEGRAM_BOT_TOKEN=7012345678:AAH...
set TELEGRAM_CHAT_ID=-1001234567890
```

**Opción alternativa: Editar settings.py directamente**

```python
# terra_antigua_project/settings.py
TELEGRAM_BOT_TOKEN = '7012345678:AAH...'   # Reemplaza con tu token
TELEGRAM_CHAT_ID   = '-1001234567890'      # Reemplaza con tu chat ID
```

---

## 📋 Estructura del proyecto

```
terra_antigua/
├── manage.py
├── requirements.txt
├── terra_antigua_project/
│   ├── settings.py          ← Configuración principal
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── models.py            ← Modelo ContactMessage
│   ├── forms.py             ← Formulario de contacto
│   ├── views.py             ← Lógica de la vista
│   ├── urls.py              ← Rutas
│   ├── admin.py             ← Panel de administración
│   └── telegram_notify.py  ← Envío de notificaciones
└── templates/
    └── core/
        └── home.html        ← Template completo del sitio
```

---

## 🎛️ Panel de administración

Visita http://127.0.0.1:8000/admin con tu superusuario para ver todos
los mensajes de contacto recibidos, filtrarlos por tour o fecha, y buscarlos.

---

## 🌐 Despliegue en producción

Para subir el sitio a un servidor real:

1. Cambia `DEBUG = False` en settings.py
2. Configura `ALLOWED_HOSTS = ['tudominio.com']`
3. Usa variables de entorno para SECRET_KEY, TOKEN y CHAT_ID
4. Corre `python manage.py collectstatic`
5. Usa Gunicorn + Nginx o Railway/Render para el hosting

---

## 💬 Formato del mensaje en Telegram

Cuando alguien llene el formulario, recibirás:

```
🏛️ Nuevo contacto en Terra Antigua
━━━━━━━━━━━━━━━━━━━━━━
👤 Nombre:   María López
📧 Email:    maria@email.com
📞 Teléfono: +52 55 1234 5678
🗺️ Tour:     Teotihuacán – Ciudad de los Dioses
💬 Mensaje:
Quisiera información sobre el tour al amanecer...
━━━━━━━━━━━━━━━━━━━━━━
🕐 15/01/2024 09:32 (CDMX)
```
