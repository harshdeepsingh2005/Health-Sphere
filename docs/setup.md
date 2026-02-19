# Setup Guide — HealthSphere AI

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| pip | 23+ |
| Git | any |
| Google Gemini API key | [Get one here](https://aistudio.google.com/) |

---

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Health-Sphere
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv

# Activate it:
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

---

## 3. Install Dependencies

```bash
pip install -r healthsphere/requirements.txt
```

---

## 4. Configure Environment Variables

```bash
cd healthsphere
cp .env.example .env   # if .env.example exists, else create .env
```

Edit `.env` with your values:

```env
# Django
SECRET_KEY=your-random-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Email (for appointment reminders)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
```

> **Get a Gemini API Key:** Go to [Google AI Studio](https://aistudio.google.com/) → Create API Key → copy into `.env`

---

## 5. Run Database Migrations

```bash
cd healthsphere   # if not already inside
python manage.py migrate
```

---

## 6. Create an Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

---

## 7. (Optional) Load Sample Data

If a fixture file is provided:

```bash
python manage.py loaddata fixtures/sample_data.json
```

---

## 8. Start the Development Server

```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

Login with your superuser credentials.

---

## Running on a Different Port

```bash
python manage.py runserver 8001
# or for all interfaces (e.g., LAN access):
python manage.py runserver 0.0.0.0:8000
```

---

## Project Directory Layout

```
Health-Sphere/
├── healthsphere/           ← Django project root (cd here before running manage.py)
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── users/
│   ├── admin_portal/
│   ├── patient_portal/
│   ├── clinical_portal/
│   ├── appointments/
│   ├── prescriptions/
│   ├── analytics/
│   ├── interoperability/
│   ├── telemedicine/
│   ├── ai_services/
│   ├── templates/
│   ├── static/
│   ├── .env                ← Your secrets (never commit)
│   ├── db.sqlite3          ← SQLite database (dev)
│   └── manage.py
├── docs/                   ← Documentation
└── README.md
```

---

## Common Issues

### `ModuleNotFoundError: No module named 'google.generativeai'`
```bash
pip install google-generativeai
```

### `GEMINI_API_KEY not found`
Check that your `.env` file is in `healthsphere/` (same folder as `manage.py`) and that the key name matches exactly.

### Database errors after pulling new code
```bash
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic
# And ensure DEBUG=True in development
```

### Port already in use
```bash
python manage.py runserver 8001
# Or kill the process using the port:
lsof -ti:8000 | xargs kill -9   # macOS/Linux
```

---

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set a strong random `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` for your domain
- [ ] Switch to PostgreSQL (`DATABASE_URL=postgres://...`)
- [ ] Run `python manage.py collectstatic`
- [ ] Use gunicorn: `gunicorn config.wsgi:application`
- [ ] Set up nginx as reverse proxy with SSL
- [ ] Store all secrets in environment variables or a secrets manager
- [ ] Configure a proper email backend (not console)
- [ ] Set up database backups
