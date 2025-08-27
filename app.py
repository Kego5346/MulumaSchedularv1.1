from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret")

db = SQLAlchemy(app)

# ------------------- Flask-Migrate ------------------- #
from flask_migrate import Migrate
migrate = Migrate(app, db)

# ------------------- Database Models ------------------- #
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")  # "admin" or "user"
    tasks = db.relationship('Task', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    backlog = db.Column(db.String(100))
    process = db.Column(db.String(100))
    done = db.Column(db.String(100))
    date = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ------------------- Flask-Login ------------------- #
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------- No-Cache Headers ------------------- #
@app.after_request
def add_no_cache_headers(response):
    """
    Prevent browser from caching pages, so logged out users
    cannot access protected pages via the Back button.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ------------------- Create DB & Default Admin ------------------- #
with app.app_context():
    db.create_all()
    if not User.query.filter_by(name="Admin", surname="User").first():
        admin = User(name="Admin", surname="User", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

# ------------------- Routes ------------------- #
@app.route('/')
@login_required
def muluma_schedular():
    tasks = Task.query.all()
    return render_template('muluma_schedular.html', tasks=tasks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']

        if User.query.filter_by(name=name, surname=surname).first():
            flash("User already exists", "danger")
            return redirect(url_for('register'))

        new_user = User(name=name, surname=surname)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']

        user = User.query.filter_by(name=name, surname=surname).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('muluma_schedular'))
        else:
            flash("Invalid name, surname, or password", "danger")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
@login_required
def add_task():
    name = request.form['name']
    surname = request.form['surname']
    backlog = request.form['backlog']
    process = request.form['process']
    done = request.form['done']
    date = request.form['date']

    new_task = Task(
        name=name,
        surname=surname,
        backlog=backlog,
        process=process,
        done=done,
        date=date,
        user_id=current_user.id
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('muluma_schedular'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)

    # Only admin or task owner can edit
    if current_user.role != 'admin' and task.user_id != current_user.id:
        flash("You do not have permission to edit this task.", "danger")
        return redirect(url_for('muluma_schedular'))

    if request.method == 'POST':
        # Only editable fields
        task.backlog = request.form['backlog']
        task.process = request.form['process']
        task.done = request.form['done']
        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for('muluma_schedular'))

    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)

    if current_user.role != 'admin' and task.user_id != current_user.id:
        flash("You do not have permission to delete this task.", "danger")
        return redirect(url_for('muluma_schedular'))

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('muluma_schedular'))

# ------------------- Run App ------------------- #
if __name__ == '__main__':
    app.run(debug=True)
