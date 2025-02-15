from app import db, app
from models import User  # ✅ Importar el modelo User
from werkzeug.security import generate_password_hash


def test_home_page(client):
    """Verifica que la página de inicio carga correctamente"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Bienvenido" in response.data  # Verifica que "Bienvenido" está en la respuesta

def test_register(client):
    """Prueba el registro de un usuario"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registro exitoso" in response.data  # Verifica el mensaje de éxito

def test_login(client):
    """Prueba el inicio de sesión"""
    # Crear usuario en la base de datos de pruebas
    with client.application.app_context():
        user = User(username="testuser", email="test@example.com", password_hash=generate_password_hash("password"))
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Dashboard" in response.data  # Verifica que accede al dashboard tras el login

def test_dashboard_requires_login(client):
    """Verifica que el acceso al dashboard sin login redirige a la página de inicio de sesión"""
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Ingresar" in response.data  # Verifica que redirige a login
