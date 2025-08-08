# Smart Thermostat Backend

This repository contains the backend API for the Smart Thermostat Automation System, a cloud-based platform for managing and automating thermostats across multiple properties.

## Features

- User authentication with JWT tokens
- Property management
- Thermostat control (Nest, Cielo, Pioneer)
- Calendar integration (Google Calendar, iCal)
- Automation scheduling
- Admin tools and reporting

## Technology Stack

- Flask (Python web framework)
- SQLite database
- JWT authentication
- RESTful API design

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/smart-thermostat-backend.git
cd smart-thermostat-backend
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python -m src.main
```

The API will be available at http://localhost:5000

## API Documentation

### Authentication

- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - Login and get access token

### Properties

- GET `/api/properties` - List all properties
- POST `/api/properties` - Create a new property
- GET `/api/properties/{id}` - Get property details
- PUT `/api/properties/{id}` - Update property
- DELETE `/api/properties/{id}` - Delete property

### Thermostats

- GET `/api/thermostats` - List all thermostats
- POST `/api/thermostats` - Add a new thermostat
- GET `/api/thermostats/{id}` - Get thermostat details
- PUT `/api/thermostats/{id}` - Update thermostat
- PUT `/api/thermostats/{id}/temperature` - Set temperature
- DELETE `/api/thermostats/{id}` - Delete thermostat

### Calendars

- GET `/api/calendars` - List all calendars
- POST `/api/calendars` - Add a new calendar
- GET `/api/calendars/{id}` - Get calendar details
- DELETE `/api/calendars/{id}` - Delete calendar

### Schedules

- GET `/api/schedules` - List all schedules
- POST `/api/schedules` - Create a new schedule
- GET `/api/schedules/{id}` - Get schedule details
- PUT `/api/schedules/{id}` - Update schedule
- DELETE `/api/schedules/{id}` - Delete schedule

## Deployment

This repository is configured for deployment on Render.

### Render Deployment

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Select the repository
4. Configure the build command: `pip install -r requirements.txt`
5. Configure the start command: `gunicorn src.main:app`
6. Set environment variables as needed

## License

MIT
