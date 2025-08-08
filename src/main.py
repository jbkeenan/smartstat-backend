import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from src.models.base import db
from src.routes.auth import auth_bp
from src.routes.properties import properties_bp
from src.routes.thermostats import thermostats_bp
from src.routes.calendars import calendars_bp
from src.routes.schedules import schedules_bp
from src.routes.admin import admin_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_12345')

# Enable CORS for frontend requests
CORS(app, resources={r"/api/*": {"origins": "https://smartstatfront.onrender.com"}})

# Switch to SQLite for deployment compatibility
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///thermostat_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(properties_bp, url_prefix='/api/properties')
app.register_blueprint(thermostats_bp, url_prefix='/api/thermostats')
app.register_blueprint(calendars_bp, url_prefix='/api/calendars')
app.register_blueprint(schedules_bp, url_prefix='/api/schedules')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@app.route('/')
def index():
    return jsonify({
        'name': 'Smart Thermostat Automation System API',
        'version': '1.0.0',
        'status': 'online'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected'
    })

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
