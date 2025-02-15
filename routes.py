from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from models import User, Task
from flask import current_app
from urllib.parse import urlparse, urljoin


@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return db.session.get(User, int(user_id))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not username or not email or not password:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('register'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('El correo ya está registrado', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Registro exitoso, ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard')

            return redirect(next_page)
        else:
            flash('Credenciales incorrectas', 'danger')

    return render_template('login.html')


# @app.route('/dashboard')
# @login_required
# def dashboard():
#     search_query = request.args.get('search', '').strip()  # Obtener el parámetro de búsqueda

#     if current_user.is_admin:
#         tasks = Task.query
#     else:
#         tasks = Task.query.filter_by(user_id=current_user.id)

#     # Si hay un término de búsqueda, filtrar por título o descripción o usuario
#     if search_query:
#         tasks = tasks.filter(
#             (Task.title.ilike(f"%{search_query}%")) | 
#             (Task.description.ilike(f"%{search_query}%"))
#         )

#     tasks = tasks.all()  # Ejecutar la consulta

#     return render_template('dashboard.html', tasks=tasks, search_query=search_query)


@app.route('/dashboard')
@login_required
def dashboard():
    search_query = request.args.get('search', '').strip()  # Obtener el parámetro de búsqueda

    if current_user.is_admin:
        tasks = Task.query.all()  # Obtener todas las tareas si es admin
        users = User.query.all()  # Obtener todos los usuarios para asignar tareas
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        users = []  # No enviar la lista de usuarios a los usuarios normales

    return render_template('dashboard.html', tasks=tasks, users=users, search_query=search_query)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    title = request.form['title'].strip()
    description = request.form['description'].strip()

    if not title:
        flash('El título de la tarea es obligatorio', 'danger')
        return redirect(url_for('dashboard'))

    new_task = Task(title=title, description=description, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()

    flash('Tarea agregada con éxito', 'success')
    return redirect(url_for('dashboard'))

@app.route('/toggle_task/<int:task_id>')
@login_required
def toggle_task(task_id):
    task = db.session.get(Task, task_id)

    if task and (current_user.is_admin or task.user_id == current_user.id):
        task.completed = not task.completed
        db.session.commit()
        flash("Estado de la tarea actualizado.", "success")

    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)

    if task and (current_user.is_admin or task.user_id == current_user.id):
        db.session.delete(task)
        db.session.commit()
        flash("Tarea eliminada correctamente.", "success")

    return redirect(url_for('dashboard'))


@app.route('/assign_task/<int:task_id>', methods=['POST'])
@login_required
def assign_task(task_id):
    if not current_user.is_admin:
        flash("No tienes permisos para asignar tareas.", "danger")
        return redirect(url_for('dashboard'))

    task = db.session.get(Task, task_id)
    if not task:
        flash("Tarea no encontrada.", "danger")
        return redirect(url_for('dashboard'))

    user_id = request.form.get('user_id')
    user = db.session.get(User, user_id)

    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('dashboard'))

    task.user_id = user.id
    db.session.commit()

    flash(f"Tarea '{task.title}' asignada a {user.username}.", "success")
    return redirect(url_for('dashboard'))


@app.route('/edit_task/<int:task_id>', methods=['POST'])
@login_required
def edit_task(task_id):
    task = db.session.get(Task, task_id)

    if task and (current_user.is_admin or task.user_id == current_user.id):
        task.title = request.form['title'].strip()
        task.description = request.form['description'].strip()
        db.session.commit()
        flash("Tarea actualizada correctamente.", "success")

    return redirect(url_for('dashboard'))


@app.route('/edit_task/<int:task_id>', methods=['GET'])
@login_required
def edit_task_form(task_id):
    task = db.session.get(Task, task_id)

    if not task or (not current_user.is_admin and task.user_id != current_user.id):
        flash("No tienes permiso para editar esta tarea.", "danger")
        return redirect(url_for('dashboard'))

    return render_template('edit.html', task=task)

@app.route('/users')
@login_required
def users():
    if current_user.is_admin:
        users = User.query.all()
    else:
        users = []

    return render_template('users.html', users=users)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()

        if not username or not email:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('profile'))

        # Verificar si el nombre de usuario ya está en uso por otro usuario
        existing_username = User.query.filter(User.username == username, User.id != current_user.id).first()
        if existing_username:
            flash('El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('profile'))

        # Verificar si el correo ya está en uso por otro usuario
        existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_email:
            flash('El correo ya está registrado por otro usuario.', 'danger')
            return redirect(url_for('profile'))

        try:
            # ✅ ACTUALIZAR LOS DATOS DEL USUARIO
            user = User.query.get(current_user.id)
            user.username = username
            user.email = email

            db.session.commit()

            # ✅ FORZAR ACTUALIZACIÓN DE LA SESIÓN DE USUARIO
            flash('Perfil actualizado con éxito.', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el perfil: {str(e)}', 'danger')

    return render_template('profile.html', user=User.query.get(current_user.id))


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if not check_password_hash(current_user.password_hash, current_password):
        flash('Contraseña actual incorrecta.', 'danger')
        return redirect(url_for('profile'))

    if new_password != confirm_password:
        flash('Las nuevas contraseñas no coinciden.', 'danger')
        return redirect(url_for('profile'))

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('Contraseña actualizada correctamente.', 'success')

    return redirect(url_for('profile'))