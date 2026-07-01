from flask import Flask, redirect, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from modell import db, User, TodoList
from flask_login import LoginManager, logout_user, login_user, login_required, current_user
from form import RegisterForm, LoginForm, TodoForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'HARSH123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,                # ✅ Add this line
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful, please login.")
        return redirect(url_for('login'))
    return render_template("registration.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = TodoForm()
    if form.validate_on_submit():
        todo = TodoList(content=form.content.data, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('dashboard'))
    todos = TodoList.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', form=form, todos=todos)

if __name__ == "__main__":
    app.run(debug=True)
