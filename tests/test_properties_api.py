import pytest
import json
from src.models.property import Property
from src.models.user import User, UserRole

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
def auth_headers(test_user):
    """Generate auth headers for the test user"""
    from src.routes.auth import JWT_SECRET, JWT_ALGORITHM
    import jwt
    from datetime import datetime, timedelta
    
    token_payload = {
        'user_id': test_user.id,
        'email': test_user.email,
        'role': test_user.role.value,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_property(db_session, test_user):
    """Create a test property"""
    property = Property(
        name='Test Property',
        address='123 Main St',
        city='Testville',
        state='TS',
        zip_code='12345',
        country='Testland',
        user_id=test_user.id
    )
    db_session.add(property)
    db_session.commit()
    return property

def test_get_properties(client, auth_headers, test_property):
    """Test getting properties for a user"""
    response = client.get('/api/properties/', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'properties' in data
    assert len(data['properties']) == 1
    assert data['properties'][0]['name'] == 'Test Property'

def test_get_property(client, auth_headers, test_property):
    """Test getting a specific property"""
    response = client.get(f'/api/properties/{test_property.id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'property' in data
    assert data['property']['name'] == 'Test Property'
    assert data['property']['address'] == '123 Main St'

def test_create_property(client, auth_headers):
    """Test creating a new property"""
    response = client.post('/api/properties/', headers=auth_headers, json={
        'name': 'New Property',
        'address': '456 Oak St',
        'city': 'Newville',
        'state': 'NS',
        'zip_code': '67890',
        'country': 'Newland'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'property' in data
    assert data['property']['name'] == 'New Property'
    assert data['property']['address'] == '456 Oak St'

def test_update_property(client, auth_headers, test_property):
    """Test updating a property"""
    response = client.put(f'/api/properties/{test_property.id}', headers=auth_headers, json={
        'name': 'Updated Property',
        'address': 'Updated Address'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'property' in data
    assert data['property']['name'] == 'Updated Property'
    assert data['property']['address'] == 'Updated Address'
    # Fields not included in the update should remain unchanged
    assert data['property']['city'] == 'Testville'

def test_delete_property(client, auth_headers, test_property):
    """Test deleting a property"""
    response = client.delete(f'/api/properties/{test_property.id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # Verify property is deleted
    response = client.get(f'/api/properties/{test_property.id}', headers=auth_headers)
    assert response.status_code == 404

def test_unauthorized_access(client, test_property):
    """Test accessing properties without authentication"""
    response = client.get('/api/properties/')
    assert response.status_code == 401
    
    response = client.get(f'/api/properties/{test_property.id}')
    assert response.status_code == 401
    
    response = client.post('/api/properties/', json={
        'name': 'New Property',
        'address': '456 Oak St',
        'city': 'Newville',
        'state': 'NS',
        'zip_code': '67890',
        'country': 'Newland'
    })
    assert response.status_code == 401
