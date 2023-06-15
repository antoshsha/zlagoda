from flask import Flask, render_template, redirect, url_for, request, session, flash
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


def manager_access():
    if not session.get("manager"):
        flash("Access denied")
        return redirect(url_for('home'))


def cashier_access():
    if not session.get("cashier"):
        flash("Access denied")
        return redirect(url_for('home'))

def login_user(username, password):
    # Перевірка введених облікових даних
    if username == 'admin' and password == '1':
        session['logged_in'] = True
        session["manager"] = True
        session["cashier"] = True
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def start():
    return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    role= request.args.get("role")
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    role = ""
    if session.get("manager"):
        role = "менеджер!"
    else:
        role = "касир"
    return render_template('home.html', role=role)


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
    session["manager"] = False
    session["cashier"] = False
    return redirect(url_for('login'))



#------------------------------- ALL FOR MANAGER
@app.route('/manager_cabinet', methods=['GET', 'POST'])
def manager_cabinet():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    if not session.get("manager"):
        return redirect(url_for('home'))
    return render_template('manager_cabinet.html')

#----------------------- ADD
@app.route('/add_empl', methods=['GET', 'POST'])
def add_empl():
    if not session.get("manager"):
        return redirect(url_for('home'))
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
            request.form.get('percent'),
        ]
        print(data)  # Виведення даних на консоль (для перевірки)
        # Опрацьовка даних та збереження в базу даних
        customer_card.insert_customer_card(data)
        return redirect(url_for('manager_cabinet'))  # Перенаправлення на сторінку кабінету менеджера
    role=0
    if session.get("manager"):
        role=1
    return render_template('manager_options/add_customer_card.html', role=role)


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        # Опрацьовка даних та збереження в базу даних
        category.insert_category(category_name)
        return redirect(url_for('manager_cabinet'))  # Перенаправлення на сторінку кабінету менеджера

    return render_template('manager_options/add_category.html')


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not session.get("manager"):
        return redirect(url_for('home'))
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
    if not session.get("manager"):
        return redirect(url_for('home'))
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
    if not session.get("manager"):
        return redirect(url_for('home'))
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
    if not session.get('logged_in'):      #спільне для касира і менеджера
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

        return redirect(url_for('manager_cabinet'), role=session.get("manager"))
    role = 0
    if session.get("manager"):
        role = 1
    return render_template('manager_options/update_customer_card.html',role=role)


@app.route('/update_category', methods=['GET', 'POST'])
def update_category():
    if not session.get("manager"):
        return redirect(url_for('home'))
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
    if not session.get("manager"):
        return redirect(url_for('home'))
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
    if not session.get("manager"):
        return redirect(url_for('home'))
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

#--------------------- DELETE

@app.route('/delete_employee', methods=['POST', 'GET'])
def delete_employee():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    if request.method == 'POST':
        employee_id = request.form.get('id_employee')
        employee.delete_employee(employee_id)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/delete_employee.html')


@app.route('/delete_customer_card', methods=['POST', 'GET'])
def delete_customer_card():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    if request.method == 'POST':
        card_number = request.form.get('card_number')
        customer_card.delete_customer_card(card_number)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/delete_customer_card.html')


@app.route('/delete_category', methods=['POST', 'GET'])
def delete_category():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    if request.method == 'POST':
        category_number = request.form.get('category_number')
        category.delete_category(category_number)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/delete_category.html')


@app.route('/delete_product', methods=['POST', 'GET'])
def delete_product():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product.delete_product(product_id)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/delete_product.html')


@app.route('/delete_product_store', methods=['POST', 'GET'])
def delete_product_store():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    if request.method == 'POST':
        upc = request.form.get('upc')
        store_product.delete_store_product(upc)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/delete_product_store.html')


@app.route('/delete_check_store', methods=['POST', 'GET'])
def delete_check_store():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    if request.method == 'POST':
        check_number = request.form.get('check_number')
        checkk.delete_checkk(check_number)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/delete_checkk.html')

#---------------- REPORTS
@app.route('/report_employees', methods=['POST', 'GET'])
def report_employees():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    if request.method == 'GET':
        sort_by_surname = request.args.get('sort_by_surname')
        if sort_by_surname:
            employees = employee.get_all_employees_sorted_by_surname()
        else:
            employees = employee.get_all_employees()
    else:
        employees = employee.get_all_employees()

    return render_template('manager_options/report_employees.html', employees=employees)


@app.route('/report_customer_cards')
def report_customer_cards():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    try:
        cards = customer_card.get_all_customer_cards()
        return render_template('manager_options/report_customer_cards.html', cards=cards)
    except Exception as e:
        print("Error: Failed to generate customer card report -", str(e))
        return redirect(url_for('manager_cabinet'))


@app.route('/report_categories')
def report_categories():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    try:
        categories = category.get_all_categories()
        print(categories)
        return render_template('manager_options/report_categories.html', categories=categories)
    except Exception as e:
        print("Error: Failed to generate category report -", str(e))
        return redirect(url_for('manager_cabinet'))


@app.route('/report_products')
def report_products():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Отримати всі товари з бази даних
    products=product.get_all_products()

    # Передати дані товарів у шаблон і відобразити звіт
    return render_template('manager_options/report_products.html', products=products)


@app.route('/report_products_store')
def report_products_store():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Отримати всі товари в магазині з бази даних
    products=store_product.get_all_products()

    # Передати дані товарів у шаблон і відобразити звіт
    return render_template('manager_options/report_products_store.html', products=products)


@app.route('/report_checks')
def report_checks():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    checks=checkk.get_all_checks()

    return render_template('manager_options/report_checks.html', checks=checks)


@app.route('/search_by_surname', methods=['POST', "GET"])
def search_by_surname():
    if not session.get("manager"):
        return redirect(url_for('home'))
    surname = request.form.get('surname')
    phone, address=employee.get_by_surname(surname)


    return render_template('manager_options/search_by_surname.html', phone=phone, address=address)


@app.route('/search_discount', methods=['POST'])
def search_by_discount():
    if not session.get("manager"):
        return redirect(url_for('home'))
    discount = request.form['discount']

    # Perform the search query using the discount value
    cards = customer_card.get_cards_by_discount(discount)

    # Sort the cards by surname
    cards = sorted(cards, key=lambda x: x[1])

    return render_template('manager_options/report_customer_cards.html', cards=cards)



@app.route('/check_by_id', methods=['GET', 'POST'])
def check_by_id():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if request.method == 'POST':
        cashier_id = request.form['cashier_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        product_name = request.form.get('product_name', '')

        results = checkk.get_checks_by_cashier(cashier_id, start_date, end_date)
        total_quantity = sum(int(check[7]) for check in results if check[6] == product_name)
        total_sum = 0.0
        for check in results:
            if(check[4]!=""):
                total_sum += float(check[4])  # Індекс 4 - колонка "Загальна сума"
        print(results)
        return render_template('manager_options/check_by_id.html', checks=results,total_sum=total_sum, total_quantity=total_quantity)

    return render_template('manager_options/check_by_id.html', checks=[])


#----------------------------------- ALL FOR CASHIER
@app.route('/cashier_cabinet')
def cashier_cabinet():
    return render_template('cashier_cabinet.html')


@app.route('/all_products')
def all_products():
    # Retrieve the list of products from your database
    products = product.get_all_products_sorted_by_name()  # Replace with your own function to fetch products

    return render_template('cashier_optoins/all_products.html', products=products)


@app.route('/all_products_store')
def all_products_store():
    products=store_product.get_all_products_ordered_by_name()
    return render_template('cashier_optoins/all_products_store.html', products=products)


@app.route('/search_product_by_name', methods=['POST', 'GET'])
def search_product_by_name():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product=store_product.get_all_products_by_name(product_name)
        return render_template('cashier_optoins/product_by_name.html', product=product)
    product_name=""
    product = store_product.get_all_products_by_name(product_name)
    return render_template('cashier_optoins/product_by_name.html', product=product)


@app.route('/add_checkk', methods=['POST', 'GET'])
def add_checkk():
    if request.method == 'POST':
        data = [
            request.form.get('check_number'),
            request.form.get('id_employee'),
            request.form.get('card_number'),
            request.form.get('print_date'),
            request.form.get('upcs'),
            request.form.get('quantities')
        ]

        # Виклик функції insert_checkk() для занесення даних в базу даних
        checkk.insert_checkk(data)

    return render_template('cashier_optoins/add_checkk.html')

@app.route('/all_clients')
def all_clients():
    clients = customer_card.get_all_clients_sorted_by_last_name()
    return render_template('cashier_optoins/all_clients.html', clients=clients)
if __name__ == '__main__':
    app.run()
