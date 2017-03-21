from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     ValidationError)
from wtforms.validators import DataRequired, Email, Length, Regexp

from .models import Document


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class RegisterForm(FlaskForm):
    reg_number = StringField(
        'Registration number',
        validators=[Length(15, 15), Regexp('\d{6}\/17\/\d{5}')])

    def validate_reg_number(self, field):
        if Document.query.filter_by(registration_number=field.data).first():
            raise ValidationError('Заявление уже было зарегистрировано.')

class SearchForm(FlaskForm):
    keyword = StringField('Registration Number')
