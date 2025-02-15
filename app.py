from models import db, User  # ✅ Ahora sí importamos User
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

if 'pytest' not in sys.modules:
    with app.app_context():
        if not User.query.filter_by(email="william.padilla@uniminuto.edu.co").first():
            admin_user = User(
                username="admin",
                email="william.padilla@uniminuto.edu.co",
                password_hash=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario administrador creado con éxito.")

from routes import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)
