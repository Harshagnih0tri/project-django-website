from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'  # optional but recommended

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # store hashed password

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # fixed 'set.'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # fixed 'set.'

class TodoList(db.Model):
    __tablename__ = 'todolost'  # matches foreign key reference

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)  # fixed 'conent'
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    user = db.relationship('User', backref='todos')  # optional, but helpful
