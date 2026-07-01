from wtforms import StringField,PasswordField,SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired , Email,Length


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")
class LoginForm(FlaskForm):
    email = StringField('Email' , validators=[DataRequired(),Email()])
    
    password = PasswordField('Password',validators =[DataRequired(),Length(min=4)])
    submit = SubmitField('Submit')
class TodoForm(FlaskForm):
    content = StringField('New Todo',validators=[DataRequired()])
    submit = SubmitField('ADD TASK')     