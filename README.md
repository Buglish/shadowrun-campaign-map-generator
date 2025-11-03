# Shadowrun Campaign Manager & Map Generator

A full-stack Python application for managing Shadowrun characters and generating dynamic campaign maps for Game Masters and players.

## Project Objectives

This application aims to provide a comprehensive platform for Shadowrun campaigns by combining character management with dynamic map generation capabilities. The system enables players to create and maintain their characters while giving Game Masters powerful tools to build, share, and dynamically generate campaign maps.

## Features

### Player Features
- **User Authentication**: Secure login and registration system
- **Character Registration**: Create and register Shadowrun characters
- **Character Management**: View, edit, and manage character details including:
  - Attributes and skills
  - Equipment and gear
  - Cyberware and bioware
  - Character background and notes

### Game Master Features
- **Map Builder**: Intuitive interface to create custom campaign maps
- **Dynamic Map Generation**: Generate maps on the fly based on parameters
- **Map Sharing**: Share maps with players during sessions
- **Campaign Management**: Organize and manage multiple campaigns

## Technology Stack

- **Backend**: Python
  - Web framework (Django)
  - MySQL Database ORM
  - Authentication system

- **Frontend**: Python-based web framework
  - Template rendering
  - Interactive map interface
  - Responsive design

## Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)
- MySQL (optional, for production)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dnd-campaign-map-generator.git
cd dnd-campaign-map-generator
```

2. **Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
venv/bin/pip install -r requirements.txt
```

4. **Configure environment variables** (optional)
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run database migrations**
```bash
venv/bin/python manage.py migrate
```

6. **Create a superuser** (for admin access)
```bash
venv/bin/python manage.py createsuperuser
```

7. **Run the development server**
```bash
venv/bin/python manage.py runserver
```

8. **Access the application**
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin

### MySQL Configuration (Optional)

By default, the project uses SQLite for development. To use MySQL:

1. Install MySQL client library:
```bash
apt install libmysqlclient-dev pkg-config
venv/bin/pip install mysqlclient==2.2.1
```

2. Update your `.env` file:
```
USE_MYSQL=True
DB_NAME=shadowrun_campaign
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

## Project Structure

```
dnd-campaign-map-generator/
├── shadowrun_campaign/      # Main Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
├── accounts/                # User authentication app
│   ├── views.py             # Login, register, profile views
│   └── urls.py              # Account URLs
├── characters/              # Character management app
│   ├── models.py            # Character data models
│   ├── views.py             # Character CRUD views
│   └── urls.py              # Character URLs
├── maps/                    # Map building and generation app
│   ├── models.py            # Map data models
│   ├── views.py             # Map CRUD and generation views
│   └── urls.py              # Map URLs
├── campaigns/               # Campaign management app
│   ├── models.py            # Campaign data models
│   ├── views.py             # Campaign CRUD views
│   └── urls.py              # Campaign URLs
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   └── home.html            # Homepage template
├── static/                  # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── media/                   # User-uploaded files
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── .gitignore               # Git ignore rules
```

## Roadmap

### Completed
- [x] Django project structure setup
- [x] User authentication system (login/logout/register)
- [x] Basic app structure (accounts, characters, maps, campaigns)
- [x] URL routing configuration
- [x] Base templates with Bootstrap 5
- [x] Static files configuration
- [x] Database configuration (SQLite & MySQL support)

### In Progress
- [ ] Character data models (Shadowrun attributes, skills, etc.)
- [ ] Character creation and registration forms
- [ ] Character sheet interface

### Planned
- [ ] Map data models
- [ ] Basic map builder interface
- [ ] Map generation algorithms
- [ ] Real-time map sharing
- [ ] Campaign session management
- [ ] Dice rolling integration
- [ ] Combat tracker
- [ ] NPC management
- [ ] Character equipment management
- [ ] Cyberware and bioware tracking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

buglish@yahoo.com
