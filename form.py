from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

class UserForm(FlaskForm):
   name = StringField("Name", validators=[DataRequired() ])
   email = StringField("Email", validators=[DataRequired(), Email() ])
   age = IntegerField("Age", validators=[DataRequired( ), NumberRange(min=1, max=120)])
   submit = SubmitField("register")