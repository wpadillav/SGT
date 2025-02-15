import pytest
import os
from app import app, db  # ✅ Importar correctamente la app y la base de datos
from models import User

@pytest.fixture
def client():
    """Configura una base de datos en memoria para pruebas"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # ✅ Base de datos en memoria
    app.config['WTF_CSRF_ENABLED'] = False  # ✅ Desactivar CSRF para pruebas
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # ✅ Crea la base de datos en memoria
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()  # ✅ Borra la base de datos al final
