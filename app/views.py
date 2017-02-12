from flask import render_template, redirect
from app import app
from .forms import LoginForm
from flask import request


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    app.logger.debug(form.password.data)
    if form.validate_on_submit():
        if form.email.data == 'test@test.ru' and form.password.data == 'root':
            return redirect('/home')
        else:
            error = 'Error'
            return render_template('index.html', form=form, error = error)
    return render_template('index.html', title='Sign In', form=form)

@app.route('/home')
def home():
    return render_template('home.html', title='Home')
