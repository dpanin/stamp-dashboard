from flask import render_template, redirect, flash
from app import app
from .forms import LoginForm
from flask import request
from flask_login import login_required, login_user, logout_user
from .models import User


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect('/home')
        else:
            error = 'Error'
            return render_template('login.html', form=form, error=error)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из своей учетной записи.')
    return redirect('/login')