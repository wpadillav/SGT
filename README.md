Aquí tienes la **documentación completa** de tu aplicación Flask. 📄🚀  

---

# **📌 Documentación del Proyecto - Task Manager**
## **📖 Descripción**
Task Manager es una aplicación web construida con **Flask** que permite la gestión de tareas entre usuarios. Los administradores pueden asignar tareas a usuarios específicos y gestionar el estado de cada una. También cuenta con funcionalidades de autenticación, gestión de usuarios y edición de perfil.

---

## **📁 Estructura del Proyecto**
```
task_manager/
│── gen.py               # Genera una clave aleatoria segura
│── app.py               # Archivo principal que inicia la aplicación
│── config.py            # Configuración de la aplicación (Base de datos, claves, etc.)
│── models.py            # Modelos de la base de datos con SQLAlchemy
│── routes.py            # Rutas de la aplicación (login, tareas, usuarios, etc.)
│── templates/           # Archivos HTML (Frontend) 
│   │── 404.html
│   │── dashboard.html
│   │── edit.html
│   │── index.html
│   │── layout.html
│   │── login.html
│   │── profile.html
│   │── register.html
│   │── users.html
│── .env                 # Variables de entorno (Claves secretas y conexión a la BD)
│── requirements.txt     # Dependencias del proyecto
│── migrations/          # Migraciones de base de datos con Flask-Migrate
```

---

## **⚙️ Instalación y Configuración**
### **1️⃣ Clonar el repositorio**
```bash
git clone https://github.com/wpadillav/SGT.git
cd task_manager
```

### **2️⃣ Crear un entorno virtual (opcional, pero recomendado)**
```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
venv\Scripts\activate     # En Windows
```

### **3️⃣ Instalar las dependencias**
```bash
pip install -r requirements.txt
```

### **4️⃣ Configurar las variables de entorno**
Edita el archivo `.env` con los valores correctos para tu base de datos:
```
SECRET_KEY=tu_clave_secreta
SQLALCHEMY_DATABASE_URI=mariadb+mariadbconnector://usuario:contraseña@localhost/task_manager
```

### **5️⃣ Iniciar la base de datos**
Ejecuta estos comandos para crear la base de datos y aplicar las migraciones:
```bash
flask db init
flask db migrate -m "Inicialización de la BD"
flask db upgrade
```

### **6️⃣ Iniciar la aplicación**
```bash
python app.py
```
Luego, abre en el navegador:
```
http://127.0.0.1:5000/
```

---

## **🛠️ Funcionalidades**
### **📌 1. Autenticación de Usuarios**
- Registro de nuevos usuarios (`/register`)
- Inicio de sesión (`/login`)
- Cierre de sesión (`/logout`)

### **📌 2. Gestión de Tareas**
- **Crear tareas** (`/add_task`)
- **Completar/Pendiente** (`/toggle_task/<int:task_id>`)
- **Editar tarea** (`/edit_task/<int:task_id>`)
- **Eliminar tarea** (`/delete_task/<int:task_id>`)

### **📌 3. Asignación de Tareas (Solo Admin)**
- **Asignar tarea a un usuario específico** (`/assign_task/<int:task_id>`)

### **📌 4. Gestión de Usuarios**
- **Ver lista de usuarios (Solo Admin)** (`/users`)
- **Editar perfil** (`/profile`)
- **Cambiar contraseña** (`/change_password`)

---

## **📜 Explicación de los Módulos**
### **📌 `models.py` (Modelos de la Base de Datos)**
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
```
- **User**: Representa un usuario del sistema.
  - `is_admin`: Determina si un usuario es administrador.

```python
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```
- **Task**: Representa una tarea asignada a un usuario.

---

### **📌 `routes.py` (Rutas de la Aplicación)**
```python
@app.route('/register', methods=['GET', 'POST'])
def register():
```
- Permite el **registro de nuevos usuarios**.
- Verifica que el email no esté en uso.

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
```
- Permite **iniciar sesión** usando correo y contraseña.

```python
@app.route('/dashboard')
@login_required
def dashboard():
```
- **Muestra todas las tareas del usuario actual**.
- Si es administrador, muestra todas las tareas del sistema.

```python
@app.route('/assign_task/<int:task_id>', methods=['POST'])
@login_required
def assign_task(task_id):
```
- **Solo el administrador** puede asignar tareas a otros usuarios.

```python
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
```
- Permite a los usuarios **editar su nombre y correo**.

```python
@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
```
- Permite a los usuarios **cambiar su contraseña**.

---

### **📌 `app.py` (Punto de Entrada de la Aplicación)**
```python
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
```
- Inicializa Flask, la base de datos y Flask-Login.
- Crea un usuario administrador por defecto.

---

### **📌 `config.py` (Configuración de la Aplicación)**
```python
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```
- Define la **clave secreta** y la **conexión a la base de datos**.

---

## **🔑 Permisos**
- **Usuarios normales** pueden ver, agregar y completar sus propias tareas.
- **Administradores** pueden:
  - Ver todas las tareas.
  - Asignar tareas a otros usuarios.
  - Ver la lista de usuarios.

---

## **🔧 Posibles Mejoras Futuras**
✅ Subida de imágenes para perfil de usuario.  
✅ Sistema de notificaciones para asignaciones de tareas.  
✅ Implementación de API REST para consumir datos desde un frontend externo.  

---

## **📜 Licencia**
Este proyecto está bajo la licencia **MIT**. Puedes modificarlo y distribuirlo libremente.  

---