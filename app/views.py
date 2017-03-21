from datetime import datetime

from app import app, db, reds
from flask import flash, g, redirect, render_template, request, send_file
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LoginForm, RegisterForm, SearchForm
from .models import Document, User


@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect('/home')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect('/home')
        else:
            error = 'Error'
            return render_template('login.html', form=form, error=error)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из своей учетной записи.')
    return redirect('/login')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    error = None
    user = g.user
    table_results = Document.get(3)
    form = RegisterForm()
    if form.validate_on_submit():
        reg_number = form.reg_number.data
        Document.add(reg_number)
        table_results = Document.get(3)
        error = 'Success'
        return render_template(
            'home.html',
            title='Home',
            user=user,
            form=form,
            table_results=table_results,
            error=error)
    else:
        if form.reg_number.data is not None:
            error = 'Validate Error'
        return render_template(
            'home.html',
            title='Home',
            user=user,
            form=form,
            table_results=table_results,
            error=error)
    return render_template(
        'home.html',
        title='Home',
        user=user,
        form=form,
        table_results=table_results)


@app.route('/return-files/')
@login_required
def return_files():
    try:
        filedir = Document.get_csv()
        return send_file(
            filedir, as_attachment=True, attachment_filename='report.csv')
    except Exception as e:
        return str(e)


last_results = ""


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    user = g.user
    form = SearchForm()
    table_results = None
    if form.validate_on_submit():
        if form.keyword.data:
            table_results = Document.search(form.keyword.data)
            last_input = form.keyword.data
            return render_template(
                'edit.html',
                title='Edit',
                user=user,
                form=form,
                table_results=table_results)
        if request.form['status']:
            reg_number = request.form['reg_number']
            id = request.form['status']
            Document.update(reg_number, id)
    return render_template(
        'edit.html',
        title='Edit',
        user=user,
        form=form,
        table_results=table_results)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        table_results = Document.search(form.keyword.data)
        status = table_results[0][7].name
        id = table_results[0][7].id
        queue_number = reds.zrank(id, form.keyword.data) + 1
        return render_template(
            'search.html',
            title='Search',
            form=form,
            status=status,
            queue_number=queue_number,
            reg_number=form.keyword.data)
    return render_template('search.html', title='Search', form=form)
