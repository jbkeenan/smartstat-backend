import pytest
import json
import jwt
from datetime import datetime, timedelta
from src.models.user import User, UserRole
from src.routes.auth import JWT_SECRET, JWT_ALGORITHM

@pytest.fixture
def app():
    from src.main import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with flask_app.app_context():
        from src.models.base import db
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    from src.models.base import db
    with app.app_context():
        yield db.session

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role=UserRole.MANAGER
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def admin_user(db_session):
    """Create an admin user"""
    user = User(
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN
    )
    user.set_password('admin123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_token(test_user):
    """Generate a valid JWT token for the test user"""
    token_payload = {
        'user_id': test_user.id,
        'email': test_user.email,
        'role': test_user.role.value,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@pytest.fixture
def admin_token(admin_user):
    """Generate a valid JWT token for the admin user"""
    token_payload = {
        'user_id': admin_user.id,
        'email': admin_user.email,
        'role': admin_user.role.value,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def test_register_endpoint(client):
    """Test user registration endpoint"""
    response = client.post('/api/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'newpassword',
        'first_name': 'New',
        'last_name': 'User'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'newuser@example.com'
    assert data['user']['first_name'] == 'New'
    assert data['user']['last_name'] == 'User'
    assert data['user']['role'] == 'manager'

def test_login_endpoint(client, test_user):
    """Test user login endpoint"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_profile_endpoint(client, auth_token):
    """Test getting user profile"""
    response = client.get('/api/auth/profile', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'

def test_profile_no_token(client):
    """Test accessing profile without token"""
    response = client.get('/api/auth/profile')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_update_profile(client, auth_token):
    """Test updating user profile"""
    response = client.put('/api/auth/profile', headers={
        'Authorization': f'Bearer {auth_token}'
    }, json={
        'first_name': 'Updated',
        'last_name': 'Name'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['first_name'] == 'Updated'
    assert data['user']['last_name'] == 'Name'

def test_admin_get_users(client, admin_token, admin_user, test_user):
    """Test admin getting all users"""
    response = client.get('/api/auth/users', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    assert len(data['users']) == 2  # admin_user and test_user

def test_non_admin_get_users(client, auth_token):
    """Test non-admin trying to get all users"""
    response = client.get('/api/auth/users', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
