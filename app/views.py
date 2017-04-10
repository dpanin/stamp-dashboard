from app import app, reds
from flask import flash, g, redirect, render_template, request, send_file
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LoginForm, SearchForm
from .models import Document, User


@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
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
            return render_template('login.html', title='Логин', form=form, error=error)
    return render_template('login.html', title='Логин', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('Вы вышли из своей учетной записи.')
    return redirect('/login')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    """A page with recent entries, entry registration and csv export."""
    user = g.user
    # TODO Replace with decorator
    # Redirects to edit page if user doesn't have permissions.
    if user.role_id != 0:
        return redirect('/edit')
    table_results = Document.get(3)
    form = SearchForm()

    # Form validation
    if form.validate_on_submit():
        reg_number = form.reg_number.data
        results = Document.search(reg_number)
        # If entry was added before
        if results:
            flash("Ошибка! Заявление с таким номером уже существует.")
            return render_template(
                'home.html',
                title='Добавление заявления',
                user=user,
                form=form,
                table_results=table_results)
        Document.add(reg_number)
        table_results = Document.get(3)
        flash("Заявление успешно зарегистрированно.")
        return render_template(
            'home.html',
            title='Добавление заявления',
            user=user,
            form=form,
            table_results=table_results)
    # If form doesn't validate and isn't empty, then return error.
    elif form.reg_number.data is not None:
        flash("Ошибка! Проверьте введенные данные.")
        return render_template(
            'home.html',
            title='Добавление заявления',
            user=user,
            form=form,
            table_results=table_results)

    return render_template(
        'home.html',
        title='Добавление заявления',
        user=user,
        form=form,
        table_results=table_results)


@app.route('/return-files/')
@login_required
def return_files():
    """CSV download page."""
    try:
        filedir = Document.get_csv()
        return send_file(
            filedir, as_attachment=True, attachment_filename='report.csv')
    except Exception as e:
        return str(e)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """A page with entry editing tools."""
    user = g.user
    # TODO Replace with decorator
    if user.role_id == 0:
        return redirect('/home')
    form = SearchForm()
    table_results = None

    # Form validation
    if form.validate_on_submit():
        if form.reg_number.data:
            table_results = Document.search(form.reg_number.data)
            if not table_results:
                flash("Ошибка! Заявление не найдено.")
            return render_template(
                'edit.html',
                title='Редактирование заявления',
                user=user,
                form=form,
                table_results=table_results)
        # Update entry if User pressed the button.
        if request.form['status']:
            reg_number = request.form['reg_number']
            doc_id = request.form['status']
            Document.update(reg_number, doc_id)
            flash("Заявление успешно обновлено.")
    elif form.reg_number.data is not None:
        flash("Ошибка! Проверьте введенные данные.")
        return render_template(
            'edit.html',
            title='Редактирование заявления',
            user=user,
            form=form,
            table_results=table_results)

    return render_template(
        'edit.html',
        title='Редактирование заявления',
        user=user,
        form=form,
        table_results=table_results)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """A search page, which displays entry current status."""
    form = SearchForm()

    # Form validation
    if form.validate_on_submit():
        table_results = Document.search(form.reg_number.data)
        status = table_results[0][7].name
        doc_id = table_results[0][7].id
        # TODO: Change error handling
        try:
            queue_number = reds.zrank(doc_id, form.reg_number.data) + 1
        except:
            queue_number = 'Ошибка'
        return render_template(
            'search.html',
            title='Поиск',
            form=form,
            status=status,
            queue_number=queue_number,
            reg_number=form.reg_number.data)
    elif form.reg_number.data is not None:
        flash("Ошибка! Проверьте введенные данные.")
        return render_template('search.html', title='Поиск', form=form)

    return render_template('search.html', title='Поиск', form=form)
