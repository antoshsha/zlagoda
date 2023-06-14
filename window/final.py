from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import employee
import category
import checkk
import customer_card
import  manager
import product
import store_product

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

#----------------------- ADD
@app.route('/add_empl', methods=['GET', 'POST'])
def add_empl():
    if request.method == 'POST':
        data = [
            request.form.get('id_employee'),
            request.form.get('empl_surname'),
            request.form.get('empl_name'),
            request.form.get('empl_patronymic'),
            request.form.get('empl_role'),
            request.form.get('salary'),
            request.form.get('date_of_birth'),
            request.form.get('date_of_start'),
            request.form.get('phone_number'),
            request.form.get('city'),
            request.form.get('street'),
            request.form.get('zip_code')
        ]
        print(data)
        employee.insert_employee(data)
        print(data)
        employee.insert_employee(data)
        # Опрацьовка даних та збереження в базу даних
    return render_template("manager_options/add_empl.html")


@app.route('/add_customer_card', methods=['GET', 'POST'])
def add_customer_card():
    if request.method == 'POST':
        data = [
            request.form.get('card_number'),
            request.form.get('cust_surname'),
            request.form.get('cust_name'),
            request.form.get('cust_patronymic'),
            request.form.get('phone_number'),
            request.form.get('city'),
            request.form.get('street'),
            request.form.get('zip_code'),
            request.form.get('percent'),
        ]
        print(data)  # Виведення даних на консоль (для перевірки)
        # Опрацьовка даних та збереження в базу даних
        customer_card.insert_customer_card(data)
        return redirect(url_for('manager_cabinet'))  # Перенаправлення на сторінку кабінету менеджера

    return render_template('manager_options/add_customer_card.html')


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        # Опрацьовка даних та збереження в базу даних
        category.insert_category(category_name)
        return redirect(url_for('manager_cabinet'))  # Перенаправлення на сторінку кабінету менеджера

    return render_template('manager_options/add_category.html')


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        data = [
            request.form.get('category_number'),
            request.form.get('product_name'),
            request.form.get('characteristics')
        ]
        if data[1]=='':
            data[1]=None
        # Process and save the data to the database
        product.insert_product(data)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/add_product.html')


@app.route('/add_product_store', methods=['GET', 'POST'])
def add_product_store():
    if request.method == 'POST':
        data = [
            request.form.get('UPC'),
            request.form.get('UPC_prom'),
            request.form.get('id_product'),
            request.form.get('selling_price'),
            request.form.get('products_number'),
            request.form.get('promotional_product'),
        ]
        print(data)  # Printing data for verification
        # Process the data and save it to the database
        store_product.insert_store_product(data)
        return redirect(url_for('manager_cabinet'))  # Redirect to the manager's cabinet page

    return render_template('manager_options/add_product_store.html')

#--------------------- UPDATE
@app.route('/update_employee', methods=['GET', 'POST'])
def update_employee():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        updated_data = [
            request.form.get('empl_surname'),
            request.form.get('empl_name'),
            request.form.get('empl_patronymic'),
            request.form.get('empl_role'),
            request.form.get('salary'),
            request.form.get('date_of_birth'),
            request.form.get('date_of_start'),
            request.form.get('phone_number'),
            request.form.get('city'),
            request.form.get('street'),
            request.form.get('zip_code')
        ]
        employee.update_employee(employee_id,updated_data)  # Оновити дані про працівника в базі даних
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/update_employee.html')


@app.route('/update_customer_card', methods=['POST', 'GET'])
def update_customer_card():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = [
            request.form.get('card_number'),
            request.form.get('cust_surname'),
            request.form.get('cust_name'),
            request.form.get('cust_patronymic'),
            request.form.get('phone_number'),
            request.form.get('city'),
            request.form.get('street'),
            request.form.get('zip_code'),
            request.form.get('percent')
        ]

        # Опрацювання даних та оновлення в базі даних
        customer_card.update_customer_card(data)

        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/update_customer_card.html')


@app.route('/update_category', methods=['GET', 'POST'])
def update_category():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        category_number = request.form.get('category_number')
        category_name = request.form.get('category_name')

        # Опрацювання даних та оновлення в базі даних
        category.update_category(category_number, category_name)

        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/update_category.html')


@app.route('/update_product', methods=['GET', 'POST'])
def update_product():
    if request.method == 'POST':
        data = [
            request.form.get('product_name'),
            request.form.get('characteristics'),
            request.form.get('category_number'),
        ]
        # Process and save the data to the database
        product.update_product(data)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/update_product.html')


@app.route('/update_product_store', methods=['GET', 'POST'])
def update_product_store():
    if request.method == 'POST':
        data = [
            request.form.get('UPC'),
            request.form.get('UPC_prom'),
            request.form.get('id_product'),
            request.form.get('selling_price'),
            request.form.get('products_number'),
            request.form.get('promotional_product'),
        ]
        print(data)  # Printing data for verification
        # Process the data and save it to the database
        store_product.insert_store_product(data)
        return redirect(url_for('manager_cabinet'))  # Redirect to the manager's cabinet page

    return render_template('manager_options/update_product_store.html')


if __name__ == '__main__':
    app.run()
