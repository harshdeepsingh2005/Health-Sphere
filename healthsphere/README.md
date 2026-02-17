# 🏥 HealthSphere AI

<p align="center">
  <strong>A College-Level Healthcare Platform with Simulated AI Features</strong>
</p>

<p align="center">
  Built with Django • Three Separate Portals • Role-Based Access
</p>

---

## 📋 Overview

HealthSphere AI is a comprehensive healthcare management platform designed as a college-level academic project. It features three distinct portals for different user roles:

- **🏢 Hospital Administration Portal** - For hospital administrators to manage resources, patients, and staff
- **👨‍⚕️ Clinical Portal** - For doctors and nurses to access patient records and AI-powered insights
- **👤 Patient Portal** - For patients to manage appointments, view reports, and interact with AI assistant

## ✨ Key Features

### Hospital Administration
- Dashboard with hospital statistics
- Patient management
- Resource monitoring (beds, equipment)
- Staff scheduling
- Analytics dashboard

### Clinical Portal
- AI-powered patient risk insights
- Treatment journey visualization
- Emergency triage dashboard
- Medical record management
- Vital signs monitoring

### Patient Portal
- Personal health dashboard
- Appointment booking system
- Medical report upload with AI explanations
- Health risk assessment
- AI health assistant chatbot

## 🛠️ Tech Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with medical blue theme
- **AI Services**: Simulated/Mock (for demonstration)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Health-Sphere.git
cd Health-Sphere/healthsphere

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Access the Application
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
healthsphere/
├── config/              # Django project configuration
├── users/               # User authentication app
├── admin_portal/        # Hospital administration app
├── clinical_portal/     # Clinical staff app
├── patient_portal/      # Patient app
├── ai_services/         # Simulated AI services
├── templates/           # HTML templates
├── static/              # CSS, JavaScript files
├── docs/                # Documentation
├── manage.py            # Django CLI
└── requirements.txt     # Dependencies
```

## 👥 User Roles

| Role | Portal | Access |
|------|--------|--------|
| Admin | Hospital Administration | Full hospital management |
| Doctor | Clinical Portal | Patient care, records, AI insights |
| Nurse | Clinical Portal | Patient care, vitals, triage |
| Patient | Patient Portal | Personal health management |

## 🤖 AI Features (Simulated)

The platform includes simulated AI services for educational demonstration:

- **Risk Prediction**: Generates mock health risk scores
- **Triage Scoring**: ESI-based priority calculation
- **Report Explainer**: Simplifies medical terminology
- **Treatment Journey**: Predicts care milestones

> ⚠️ **Note**: AI features are simulated with mock data. They are NOT real medical predictions and should NOT be used for actual medical decisions.

## 📸 Screenshots

### Admin Dashboard
![Admin Dashboard](docs/screenshots/admin-dashboard.png)

### Clinical Portal
![Clinical Portal](docs/screenshots/clinical-portal.png)

### Patient Portal
![Patient Portal](docs/screenshots/patient-portal.png)

## 📚 Documentation

- [Architecture Documentation](docs/architecture.md)
- [Features Guide](docs/features.md)
- [Setup Instructions](docs/setup.md)

## 🧪 Testing

```bash
# Run tests
python manage.py test
```

## 🔐 Security Notice

This is an academic project. For production use, implement:
- Proper authentication (OAuth, 2FA)
- HTTPS encryption
- Database security
- Input sanitization
- Audit logging

## 📄 License

This project is for educational purposes. See [LICENSE](LICENSE) for details.

## 🤝 Contributing

This is an academic project. Contributions are welcome for learning purposes:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 👨‍💻 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Django Documentation
- Bootstrap (inspiration for UI components)
- Medical UI/UX best practices

---

<p align="center">
  Made with ❤️ for educational purposes
</p>
