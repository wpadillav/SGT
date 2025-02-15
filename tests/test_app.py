import sys
import os
import pytest
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Task

# ✅ Asegurarnos de que la ruta esté correctamente configurada
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def client():
    """ Configura una base de datos para pruebas sin borrar la principal """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite3:///test_db.sqlite'  # ✅ Base de datos persistente solo para pruebas
    app.config['WTF_CSRF_ENABLED'] = False  # ✅ Desactiva CSRF en pruebas
    client = app.test_client()

    with app.app_context():
        db.create_all()  # ✅ Crea las tablas en la base de datos de prueba

    yield client

    with app.app_context():
        db.drop_all()  # ✅ Elimina las tablas SOLO de la base de pruebas
        db.session.remove()  # ✅ Cierra la sesión para evitar errores


def test_register(client):
    """ Prueba el registro de un nuevo usuario """
    response = client.post('/register', data=dict(
        username="testuser",
        email="testuser@example.com",
        password="password"
    ), follow_redirects=True)

    assert "Iniciar Sesión" in response.data.decode("utf-8")  # ✅ Convertido a string
    assert "Registro exitoso" in response.data.decode("utf-8")  # ✅ Convertido a string

def test_login(client):
    """ Prueba el inicio de sesión con un usuario registrado """
    with app.app_context():
        hashed_password = generate_password_hash("password")
        new_user = User(username="testuser", email="testuser@example.com", password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

    response = client.post('/login', data=dict(
        email="testuser@example.com",
        password="password"
    ), follow_redirects=True)

    assert b'Dashboard' in response.data  # Verifica que llega al dashboard

def test_add_task(client):
    """ Prueba la creación de una nueva tarea """
    with app.app_context():
        hashed_password = generate_password_hash("password")
        new_user = User(username="testuser", email="testuser@example.com", password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

    client.post('/login', data=dict(email="testuser@example.com", password="password"), follow_redirects=True)

    response = client.post('/add_task', data=dict(
        title="Tarea de prueba",
        description="Descripción de la tarea"
    ), follow_redirects=True)

    assert "Tarea de prueba" in response.data.decode("utf-8")
    assert "Descripción de la tarea" in response.data.decode("utf-8")

def test_toggle_task(client):
    """ Prueba cambiar el estado de una tarea (Completada/Pendiente) """
    with app.app_context():
        hashed_password = generate_password_hash("password")
        user = User(username="testuser", email="testuser@example.com", password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        new_task = Task(title="Tarea de prueba", description="Descripción", user_id=user.id, completed=False)
        db.session.add(new_task)
        db.session.commit()

        task_id = new_task.id
        db.session.expire_all()

    client.post('/login', data=dict(email="testuser@example.com", password="password"), follow_redirects=True)

    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task is not None

    response = client.get(f'/toggle_task/{task_id}', follow_redirects=True)
    assert b"Completada" in response.data

    response = client.get(f'/toggle_task/{task_id}', follow_redirects=True)
    assert b"Pendiente" in response.data

def test_delete_task(client):
    """ Prueba eliminar una tarea """
    with app.app_context():
        hashed_password = generate_password_hash("password")
        user = User(username="testuser", email="testuser@example.com", password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        new_task = Task(title="Tarea de prueba", description="Descripción", user_id=user.id)
        db.session.add(new_task)
        db.session.commit()

        task_id = new_task.id
        db.session.expire_all()

    client.post('/login', data=dict(email="testuser@example.com", password="password"), follow_redirects=True)

    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task is not None

    response = client.get(f'/delete_task/{task_id}', follow_redirects=True)
    assert b"Tarea de prueba" not in response.data

    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task is None  # La tarea debe haber sido eliminada
