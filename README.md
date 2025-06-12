# SureFlow Inventory Management System

<div align="center">
  <img src="static/img/sureflow-logo.png" alt="SureFlow Logo" width="200">
  
  **Streamline Your Workflow**
  
  [![Django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://www.djangoproject.com/)
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)

</div>

## 📋 Overview

SureFlow is a comprehensive web-based inventory management system designed to help organizations efficiently track and manage their device assignments to employees. Built with Django and Bootstrap, it provides an intuitive interface for managing employees, devices, departments, and generating insightful reports.

## ✨ Features

### Core Functionality
- **Employee Management**: Add, edit, and manage employee records with department and position assignments
- **Device Tracking**: Comprehensive device inventory with serial numbers, types, and assignment status
- **Assignment History**: Complete audit trail of device assignments and returns
- **Department & Position Management**: Organize employees by departments and positions
- **Real-time Dashboard**: Overview of key metrics and recent activities
- **Advanced Search & Filtering**: Quickly find employees and devices with powerful search capabilities

### Security & Authentication
- **Google OAuth Integration**: Secure authentication via Google accounts
- **Session Management**: Safe login/logout functionality
- **Permission-based Access**: Admin panel for advanced management

### Reporting & Analytics
- **Export Reports**: Generate CSV reports for devices and employee assignments
- **Visual Statistics**: Dashboard with device utilization metrics
- **Assignment Analytics**: Track device allocation patterns

## 🛠️ Technology Stack

- **Backend**: Django 3.2+
- **Frontend**: HTML5, CSS3, Bootstrap 5.3
- **Database**: SQLite (default), PostgreSQL/MySQL compatible
- **Authentication**: Django Allauth with Google OAuth
- **Icons**: Bootstrap Icons
- **Forms**: Django Crispy Forms

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/sureflow-inventory.git
cd sureflow-inventory
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

5. **Run migrations**
```bash
python manage.py makemigrations inventory_app
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

8. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 📁 Project Structure

```
sureflow-inventory/
├── inventory_app/          # Main Django application
│   ├── __pycache__/       # Python cache files
│   ├── migrations/        # Database migrations
│   ├── templates/         # HTML templates
│   │   ├── inventory/     # App-specific templates
│   │   │   ├── base.html
│   │   │   ├── dashboard.html
│   │   │   ├── devices_list.html
│   │   │   ├── employees_list.html
│   │   │   └── ...
│   │   └── registration/  # Authentication templates
│   │       ├── login.html
│   │       └── logout.html
│   ├── __init__.py
│   ├── admin.py           # Django admin configuration
│   ├── apps.py            # App configuration
│   ├── forms.py           # Django forms
│   ├── models.py          # Database models
│   ├── urls.py            # URL routing
│   └── views.py           # View controllers
├── inventory_sureflow/    # Main project directory
├── inventorybackups/      # Database backups
├── inventoryproject/      # Django project settings
├── static/                # Static files (CSS, JS, images)
├── staticfiles/           # Collected static files
├── venv/                  # Virtual environment
├── .env                   # Environment variables
├── .gitignore            # Git ignore file
├── db.sqlite3            # SQLite database
├── docker-compose.yml    # Docker compose configuration
├── Dockerfile            # Docker configuration
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration

### Database Configuration
By default, SureFlow uses SQLite. To use PostgreSQL or MySQL:

1. Install the appropriate database driver:
```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install mysqlclient
```

2. Update `DATABASES` in `settings.py` or use `DATABASE_URL` in `.env`

### Google OAuth Setup
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `https://yourdomain.com/accounts/google/login/callback/`
5. Update `.env` with your credentials

## 📊 Usage Guide

### Dashboard
The dashboard provides an overview of:
- Total employees and devices
- Device assignment status
- Recent assignments
- Device type distribution

### Managing Employees
1. Navigate to **Employees** from the sidebar
2. Click **Add Employee** to create new records
3. Use search to find specific employees
4. View employee details including assigned devices
5. Edit or soft-delete employee records

### Managing Devices
1. Go to **Devices** section
2. Add devices with serial numbers and specifications
3. Assign devices to employees
4. Track assignment history
5. Return devices when needed

### Generating Reports
1. Access **Reports** from the sidebar
2. View summary statistics
3. Export device inventory or employee assignment reports as CSV

## 🔐 Security Features

- **Authentication**: Secure Google OAuth integration
- **Session Management**: Automatic session expiry
- **CSRF Protection**: Django's built-in CSRF protection
- **SQL Injection Prevention**: Django ORM protection
- **XSS Prevention**: Template auto-escaping

## 💾 Backup Strategy

The project includes an `inventorybackups/` directory for database backups. Regular backups are recommended:

```bash
# Create backup
python manage.py dumpdata > inventorybackups/backup_$(date +%Y%m%d_%H%M%S).json

# Restore from backup
python manage.py loaddata inventorybackups/backup_20240101_120000.json
```

## 🐳 Docker Support

### Docker Setup
The project includes Docker configuration for easy deployment:

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Run migrations in Docker**
```bash
docker-compose exec web python manage.py migrate
```

3. **Create superuser in Docker**
```bash
docker-compose exec web python manage.py createsuperuser
```

### Docker Configuration Files
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-container orchestration

## 🚀 Deployment

### Heroku Deployment
1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn your_project.wsgi
```

3. Create `runtime.txt`:
```
python-3.9.16
```

4. Deploy:
```bash
heroku create your-app-name
heroku config:set SECRET_KEY='your-secret-key'
git push heroku main
heroku run python manage.py migrate
```

### Traditional Server Deployment
1. Set up Nginx/Apache
2. Configure Gunicorn/uWSGI
3. Set up SSL certificates
4. Configure static file serving
5. Set up database backups

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home/redirect to login |
| `/dashboard/` | GET | Main dashboard |
| `/employees/` | GET | List all employees |
| `/employees/add/` | GET/POST | Add new employee |
| `/employees/<id>/` | GET | Employee details |
| `/devices/` | GET | List all devices |
| `/devices/<id>/assign/` | GET/POST | Assign device |
| `/reports/export/` | GET | Export CSV reports |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Write tests for new features
- Update documentation
- Ensure backward compatibility

## 🐛 Known Issues

- Mobile responsiveness for complex tables needs improvement
- Bulk import feature not yet implemented
- Email notifications pending implementation

## 📅 Roadmap

- [ ] Email notifications for device assignments
- [ ] Bulk import/export functionality
- [ ] Device maintenance scheduling
- [ ] QR code generation for devices
- [ ] Mobile application
- [ ] REST API for third-party integrations
- [ ] Advanced analytics dashboard
- [ ] Multi-language support



## 👥 Authors

- Edwin Francis - *Initial work* - https://github.com/edwin14631

## 🙏 Acknowledgments

- Django community for excellent documentation
- Bootstrap team for the UI framework
- Contributors and testers



