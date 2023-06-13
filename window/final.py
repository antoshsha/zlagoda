from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'  # Встановіть секретний ключ для захисту форми
app.config['WTF_I18N_ENABLED'] = True  # Включення локалізації WTForms
logged = False


class LoginForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')


def login_user(username, password):
    # Перевірка введених облікових даних
    if username == 'admin' and password == '1':
        session['logged_in'] = True
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def start():
    return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('home'))  # Перенаправлення на головну сторінку, якщо користувач уже увійшов в систему

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if login_user(username, password):
            return redirect(url_for('home'))  # Перенаправлення на головну сторінку при успішному вході
        else:
            return render_template('login.html', form=form, error='Невірне ім\'я користувача або пароль')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Видалення змінної сеансу для виходу з системи
    return redirect(url_for('login'))


@app.route('/manager_cabinet', methods=['GET', 'POST'])
def manager_cabinet():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    return render_template('manager_cabinet.html')


@app.route('/add_empl', methods=['GET', 'POST'])
def add_empl():
    if request.method == 'POST':
        data = {
            'id_employee': request.form.get('id_employee'),
            'empl_surname': request.form.get('empl_surname'),
            'empl_name': request.form.get('empl_name'),
            'empl_patronymic': request.form.get('empl_patronymic'),
            'empl_role': request.form.get('empl_role'),
            'salary': request.form.get('salary'),
            'date_of_birth': request.form.get('date_of_birth'),
            'date_of_start': request.form.get('date_of_start'),
            'phone_number': request.form.get('phone_number'),
            'city': request.form.get('city'),
            'street': request.form.get('street'),
            'zip_code': request.form.get('zip_code')
        }
        print("Отримані дані:", data)
    return render_template("add_empl.html")


if __name__ == '__main__':
    app.run()
