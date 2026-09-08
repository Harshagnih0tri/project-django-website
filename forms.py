from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(check_deliverability=False)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(check_deliverability=False)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description")
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)], places=2)
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField("Image URL")
    submit = SubmitField("Save Product")


class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField("Shipping Address", validators=[DataRequired(), Length(max=300)])
    submit = SubmitField("Place Order")
