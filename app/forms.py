from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp

from .models import Document


class LoginForm(FlaskForm):
    """Login forms."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class RegisterForm(FlaskForm):
    """Register forms."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    level = IntegerField('Level', validators=[DataRequired()])



class SearchForm(FlaskForm):
    """Entry registration forms."""
    reg_number = StringField(
        'Registration number',
        validators=[Length(15, 15), Regexp('\d{6}\/17\/\d{5}')], default=None)
