from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from datetime import date
# import sys
# sys.path.append(r'D:/Мої документи/2YearNaukma/Summer/zlagoda')
import employee
import category
import checkk
import customer_card
import  manager
import product
import store_product
import encrypter
import user
from employee import conn
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'  # Встановіть секретний ключ для захисту форми
app.config['WTF_I18N_ENABLED'] = True  # Включення локалізації WTForms
logged = False


class LoginForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')


def check_role(login, password):
    try:
        cursor = employee.conn.cursor()
        cursor.execute(
            "SELECT e.empl_role FROM Employee e JOIN User u ON e.id_employee = u.id_employee WHERE u.login = ? AND u.password = ?",
            (login, password))
        result = cursor.fetchone()
        cursor.close()

        if result:
            role = result[0]
            print(result[0])
            return role
        else:
            return "not_find"
    except Exception as e:
        print("Error: Unable to fetch role -", str(e))
        return "not_find"


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
    try:
        if username == 'admin' and password == '1':
            session['logged_in'] = True
            session["manager"] = True
            session["cashier"] = True
            session["id"] = "EMP001"
            return True
        cursor = employee.conn.cursor()
        print("trying "+str(username)+" "+(str(password)))
        cursor.execute("SELECT * FROM User WHERE login = ? AND password = ?",
                       (str(username), (str(password))))
        result = cursor.fetchone()
        cursor.close()
        print(result)
        if result:
            session['logged_in'] = True
            session["id"]=result[2]
            print("session id: "+str(result[2]))
            return True
        else:
            return False
    except Exception as e:
        print("Error: Unable to authenticate user -", str(e))
        return False


    return False


@app.route('/', methods=['GET', 'POST'])
def start():
    return redirect(url_for('home'))

# @app.route('/home', methods=['GET', 'POST'])
# def home():
#     role= request.args.get("role")
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
#     role = ""
#     if session.get("manager"):
#         role = "менеджер!"
#     else:
#         role = "касир"
#     return render_template('home.html', role=role)

@app.route('/home', methods=['GET', 'POST'])
def home():
    role= request.args.get("role")
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    role = ""
    if session.get("manager"):
     employees = employee.get_all_employees()
     role = "менеджер!"
     return render_template('manager_cabinet.html', role=role, employees=employees)
    else:
        role = "касир"
        id = session.get("id")
        data = employee.get_by_id(id)
        options = customer_card.get_dropdown_customer_cards()
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        card_number = card_number.strip('()')
        card_number = card_number.split(', ')
        card_number = card_number[0][1:-1]
        data = [
            request.form.get('check_number'),
            request.form.get('id_employee'),
           card_number,
            request.form.get('print_date'),
            request.form.get('upcs'),
            request.form.get('quantities')
        ]

        # Call insert_checkk() function to store data in the database
        checkk.insert_checkk(data)

    id = session.get("id")
    data = employee.get_by_id(id)
    return render_template('cashier_cabinet.html',role = role, data=data, options = options)
 



@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        if session.get('manager'):
            return render_template('manager_cabinet.html')
        elif session.get('cashier'):
            return render_template('cashier_cabinet.html')  # Перенаправлення на головну сторінку, якщо користувач уже увійшов в систему

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if login_user(username, encrypter.xor_encrypt_decrypt(str(password))):
            print(login_user(username,password))
            if check_role(username,encrypter.xor_encrypt_decrypt(str(password)))=="Manager":
                session['manager']=True
                session['cashier']=False
            if check_role(username,encrypter.xor_encrypt_decrypt(str(password)))=="Cashier":
                session['manager']=False
                session['cashier']=True
            return redirect(url_for('home'))  # Перенаправлення на головну сторінку при успішному вході
        else:
            return render_template('login.html', form=form, error='Невірне ім\'я користувача або пароль')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    # session.pop('logged_in', None)  # Видалення змінної сеансу для виходу з системи
    # session["manager"] = False
    # session["cashier"] = False
    session.clear()
    return redirect(url_for('login'))




@app.route('/manager_cabinet', methods=['GET', 'POST'])
def manager_cabinet():
    if not session.get("manager"):
        return redirect(url_for('login'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'GET':
        sort_by_surname = request.args.get('sort_by_surname')
        if sort_by_surname:
            employees = employee.get_all_employees_sorted_by_surname()
        else:
            employees = employee.get_all_employees()
    else:
        employees = employee.get_all_employees()

    return render_template('manager_cabinet.html', employees=employees)

@app.route('/category')
@app.route('/Category/report_categories')
def go_category():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.path == '/category':
        return render_template('/manager_options/Category/category.html')
    else:
        try:
            categories = category.get_all_categories()
            return render_template('/manager_options/Category/category.html', categories=categories)
        except Exception as e:
            print("Error: Failed to generate category report -", str(e))
            return redirect(url_for('category'))

#------------------------------- BASIC MENU(CHANGES POSSIBLE)
# @app.route('/category')
# def go_category():
#     return render_template('/manager_options/Category/category.html')

# @app.route('/check')
# def go_check():
#     return render_template('/manager_options/Check/check.html')

@app.route('/check')
@app.route('/Check/report_checks')
def go_check():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.path == '/check':
        return render_template('/manager_options/Check/check.html')
    else:
        checks = checkk.get_all_checks()
        return render_template('manager_options/Check/check.html', checks=checks)


# @app.route('/customers')
# def go_customers():
#     return render_template('/manager_options/Customers/customers.html')

@app.route('/customers')
@app.route('/Customers/report_customer_cards')
def go_customers():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        cards = customer_card.get_all_customer_cards()
        return render_template('/manager_options/Customers/customers.html', cards=cards)
    except Exception as e:
        print("Error: Failed to generate customer card report -", str(e))
        return redirect(url_for('go_customers'))

@app.route('/employee')
def go_employee():
    return render_template('/manager_options/Employee/employee.html')


@app.route('/product')
@app.route('/Product/report_products')
def go_product():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Отримати всі товари з бази даних
    products = product.get_all_products()

    # Передати дані товарів у шаблон і відобразити звіт
    return render_template('/manager_options/Product/product.html', products=products)

@app.route('/product_store')
@app.route('/Product_store/report_products_store')
def go_product_store():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Отримати всі товари в магазині з бази даних
    products = store_product.get_all_products()

    # Передати дані товарів у шаблон і відобразити звіт
    role = 0
    if session.get("manager"):
        role = 1
    return render_template('/manager_options/Product_store/product_store.html', products = products)
# @app.route('/product_store')
# def go_product_store():
#     return render_template('/manager_options/Product_store/product_store.html')
# @app.route('/Product_store/report_products_store')
# def report_products_store():    #спільне для касира і менеджера
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))

#     # Отримати всі товари в магазині з бази даних
#     products=store_product.get_all_products()

#     # Передати дані товарів у шаблон і відобразити звіт
#     role = 0
#     if session.get("manager"):
#         role = 1
#     return render_template('manager_options/Product_store/report_products_store.html', products=products, role=role)




#------------------------------- CATEGORY

@app.route('/Category/add_category', methods=['GET', 'POST'])
def add_category():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        # Опрацьовка даних та збереження в базу даних
        category.insert_category(category_name)
        return redirect(url_for('go_category'))  # Перенаправлення на сторінку кабінету менеджера

    return render_template('manager_options/Category/add_category.html')

@app.route('/Category/update_category', methods=['GET', 'POST'])
def update_category():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    options = category.get_all_categories()

    if request.method == 'POST':
        category_number = request.form.get('category_number')
        comma_index = category_number.index(',')
        category_number = category_number[1:comma_index].strip()
        category_number = int(category_number)
        category_name = request.form.get('category_name')

        # Опрацювання даних та оновлення в базі даних
        category.update_category(category_number, category_name)

        return redirect(url_for('go_category'))

    return render_template('manager_options/Category/update_category.html', options = options)

@app.route('/Category/delete_category', methods=['POST', 'GET'])
def delete_category():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    options = category.get_all_categories()
    if request.method == 'POST':
        category_number = request.form.get('category_number')
        comma_index = category_number.index(',')
        category_number = category_number[1:comma_index].strip()
        category_number = int(category_number)
        category.delete_category(category_number)
        return redirect(url_for('go_category'))

    return render_template('manager_options/Category/delete_category.html', options = options)

    
@app.route('/Category/anton_mar_2', methods=['GET', 'POST'])
def mar_custom_2():
    cursor = conn.cursor()
    query = '''
            SELECT C.category_number, C.category_name
            FROM Category C
            WHERE EXISTS (
             SELECT P.id_product
             FROM Product P
             WHERE P.category_number = C.category_number
            )
            AND NOT EXISTS (
                SELECT P.id_product
                FROM Product P
                WHERE P.category_number = C.category_number
             AND NOT EXISTS (
                   SELECT S.UPC
                   FROM Store_Product S
                   WHERE S.id_product = P.id_product
             )
            )

        '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return render_template('manager_options/Category/query_mar_2.html', data=results)

@app.route('/Category/gryn_2', methods=['GET', 'POST'])
def gryn_custom_2():
    if request.method == 'POST':
        cursor = conn.cursor()
        query = '''
            SELECT category_number, category_name
            FROM Category
            WHERE EXISTS (
                SELECT *
                FROM Product
                WHERE category_number = Category.category_number
            )
            AND NOT EXISTS (
                SELECT *
                FROM Product
                WHERE category_number = Category.category_number
                AND id_product NOT IN (
                    SELECT id_product
                    FROM Store_Product
                    WHERE selling_price > ?
                )
            );
        '''
        parameter_value = float(request.form.get('parameter'))
        cursor.execute(query, (parameter_value,))
        results = cursor.fetchall()
        cursor.close()

        return render_template('manager_options/Category/query_gryn_2.html', data=results, submitted=True)
    else:
        return render_template('manager_options/Category/query_gryn_2.html', submitted=False)

#------------------------------- CHECK
@app.route('/Check/delete_check_store', methods=['POST', 'GET'])
def delete_check_store():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    options = checkk.get_dropdown_checks()
    if request.method == 'POST':
        check_number = request.form.get('check_number')
        check_number = check_number.strip('()')
        check_number = check_number.split(', ')
        check_number = check_number[0][1:-2]
        checkk.delete_checkk(check_number)
        return redirect(url_for('go_check'))

    return render_template('manager_options/Check/delete_checkk.html', options = options)

# @app.route('/Check/report_checks')
# def report_checks():
#     if not session.get("manager"):
#         return redirect(url_for('home'))
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

#     checks=checkk.get_all_checks()

#     return render_template('manager_options/Check/report_checks.html', checks=checks)

@app.route('/Check/check_by_id', methods=['GET', 'POST'])
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
        return render_template('manager_options/Check/check_by_id.html', checks=results,total_sum=total_sum, total_quantity=total_quantity)

    return render_template('manager_options/Check/check_by_id.html', checks=[])

# #----------------------- CUSTOMERS

@app.route('/Customers/add_customer_card', methods=['GET', 'POST'])
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
    return render_template('manager_options/Customers/add_customer_card.html', role=role)

@app.route('/Customers/update_customer_card', methods=['POST', 'GET'])
def update_customer_card():
    if not session.get('logged_in'):      #спільне для касира і менеджера
        return redirect(url_for('login'))
    options = customer_card.get_dropdown_customer_cards()
    if request.method == 'POST':
       
        card_number = request.form.get('card_number')
        card_number = card_number.strip('()')
        card_number = card_number.split(', ')
        card_number = card_number[0][1:-1]
        data = [
            card_number,
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

        return redirect(url_for('go_category'))
    role = 0
    if session.get("manager"):
        role = 1
    return render_template('manager_options/Customers/update_customer_card.html',role=role, options = options)

@app.route('/Customers/delete_customer_card', methods=['POST', 'GET'])
def delete_customer_card():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    options = customer_card.get_dropdown_customer_cards()
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        card_number = card_number.strip('()')
        card_number = card_number.split(', ')
        card_number = card_number[0][1:-1]
        customer_card.delete_customer_card(card_number)
        return redirect(url_for('go_customers'))

    return render_template('manager_options/Customers/delete_customer_card.html', options = options)

@app.route('/Customers/search_discount', methods=['POST'])
def search_by_discount():
    if not session.get("manager"):
        return redirect(url_for('home'))
    discount = request.form['discount']

    # Perform the search query using the discount value
    cards = customer_card.get_cards_by_discount(discount)

    # Sort the cards by surname
    cards = sorted(cards, key=lambda x: x[1])

    return render_template('manager_options/Customers/report_customer_cards.html', cards=cards)

@app.route('/Customers/report_customer_cards')
def report_customer_cards():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

    try:
        cards = customer_card.get_all_customer_cards()
        return render_template('manager_options/Customers/report_customer_cards.html', cards=cards)
    except Exception as e:
        print("Error: Failed to generate customer card report -", str(e))
        return redirect(url_for('go_customers'))

@app.route('/Customers/anton_mar_1', methods=['GET', 'POST'])
def mar_custom_1():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        cursor = conn.cursor()
        query = '''
         SELECT CC.cust_surname, CC.cust_name, SUM(SP.selling_price) AS total_price
         FROM Customer_Card CC
         JOIN Checkk CK ON CC.card_number = CK.card_number
         JOIN Sale S ON CK.check_number = S.check_number
         JOIN Store_Product SP ON S.UPC = SP.UPC
         WHERE SP.promotional_product = 1
         GROUP BY CC.cust_surname, CC.cust_name
         HAVING SUM(S.selling_price) > ?
         '''
        cursor.execute(query, (amount,))
        results = cursor.fetchall()
        cursor.close()
        return render_template('manager_options/Customers/query_mar_1.html', data=results)
    else:
        return render_template('manager_options/Customers/query_mar_1.html')
    

# #----------------------- EMPLOYEE

@app.route('/Employee/add_empl', methods=['GET', 'POST'])
def add_empl():
    if not session.get("manager"):
        return redirect(url_for('login'))
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
            request.form.get('zip_code'),
            request.form.get('username'),
            request.form.get('password'),
        ]
        print(data)
        employee.insert_employee(data[:12])
        user.insert_user(data[12],data[13],data[0])
        # Опрацьовка даних та збереження в базу даних
    return render_template("manager_options/Employee/add_empl.html")

@app.route('/Employee/update_employee', methods=['GET', 'POST'])
def update_employee():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    options = employee.get_dropdown_employee()
    if request.method == 'POST':
        employee_id = request.form.get('id_employee')
        employee_id = employee_id.strip('()')
        employee_id = employee_id.split(', ')
        employee_id = employee_id[0][1:-1]
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
        employee.update_employee(employee_id, updated_data)  # Оновити дані про працівника в базі даних
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/Employee/update_employee.html', options = options)

@app.route('/Employee/delete_employee', methods=['POST', 'GET'])
def delete_employee():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    options = employee.get_dropdown_employee()
    if request.method == 'POST':
        employee_id = request.form.get('id_employee')
        employee_id = employee_id.strip('()')
        employee_id = employee_id.split(', ')
        employee_id = employee_id[0][1:-1]
        employee.delete_employee(employee_id)
        return redirect(url_for('manager_cabinet'))

    return render_template('manager_options/Employee/delete_employee.html', options = options)

# @app.route('/Employee/report_employees', methods=['POST', 'GET'])
# def report_employees():
#     if not session.get("manager"):
#         return redirect(url_for('home'))
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

#     if request.method == 'GET':
#         sort_by_surname = request.args.get('sort_by_surname')
#         if sort_by_surname:
#             employees = employee.get_all_employees_sorted_by_surname()
#         else:
#             employees = employee.get_all_employees()
#     else:
#         employees = employee.get_all_employees()

#     return render_template('manager_options/Employee/report_employees.html', employees=employees)

# @app.route('/Employee/report_employees', methods=['POST', 'GET'])
# def report_employees():
#     if not session.get("manager"):
#         return redirect(url_for('home'))
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему

#     if request.method == 'GET':
#         sort_by_surname = request.args.get('sort_by_surname')
#         if sort_by_surname:
#             employees = employee.get_all_employees_sorted_by_surname()
#         else:
#             employees = employee.get_all_employees()
#     else:
#         employees = employee.get_all_employees()

#     return render_template('manager_options/Employee/report_employees.html', employees=employees)



@app.route('/Employee/search_by_surname', methods=['POST', "GET"])
def search_by_surname():
    if not session.get("manager"):
        return redirect(url_for('home'))
    surname = request.form.get('surname')
    phone, address=employee.get_by_surname(surname)


    return render_template('manager_options/Employee/search_by_surname.html', phone=phone, address=address)

@app.route('/Employee/hoh_1', methods=['GET', 'POST'])
def hoh_custom_1():
    if request.method == 'POST':
        cursor = conn.cursor()
        query = '''
            SELECT E.id_employee, E.empl_name, E.empl_surname
            FROM Employee E
            WHERE E.empl_role = 'Cashier' AND E.id_employee NOT IN (
                SELECT C.id_employee
                FROM Checkk C
                WHERE C.check_number IN (
                    SELECT S.check_number
                    FROM Sale S
                    WHERE S.UPC IN (
                        SELECT SP.UPC
                        FROM Store_Product SP
                        WHERE SP.id_product = (
                            SELECT P.id_product
                            FROM Product P
                            WHERE P.product_name = ?
                        )
                    )
                )
            )
            AND E.id_employee NOT IN (
                SELECT C.id_employee
                FROM Checkk C
                WHERE C.print_date = ?
            );
        '''
        product_name = str(request.form.get('product'))
        date_string = request.form.get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d').date().strftime('%Y-%m-%d')
        cursor.execute(query, (product_name, date))
        results = cursor.fetchall()
        cursor.close()

        return render_template('manager_options/Employee/query_hoh_1.html', data=results, submitted=True)
    else:
        return render_template('manager_options/Employee/query_hoh_1.html', submitted=False)


@app.route('/Employee/hoh_2', methods=['GET', 'POST'])
def hoh_custom_2():
    cursor = conn.cursor()
    query = '''
            SELECT E.city
            FROM Employee E
            INNER JOIN Checkk C ON E.id_employee = C.id_employee
            INNER JOIN Sale S ON C.check_number = S.check_number
            GROUP BY E.city
            HAVING COUNT(DISTINCT S.product_number) >= 2;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return render_template('manager_options/Employee/query_hoh_2.html', data=results, submitted=True)

# #--------------------- PRODUCT

@app.route('/Product/add_product', methods=['GET', 'POST'])
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
        return redirect(url_for('go_product'))

    return render_template('manager_options/Product/add_product.html')


@app.route('/Product/update_product', methods=['GET', 'POST'])
def update_product():
    if not session.get("manager"):
        return redirect(url_for('home'))
    options = product.get_dropdown_products()
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_name = product_name.split(",")[1].strip()
        product_name = product_name[1:-1]
        data = [
            product_name,
            request.form.get('characteristics'),
            request.form.get('category_number'),
        ]
        print(product_name)
        # Process and save the data to the database
        product.update_product(data)
        return redirect(url_for('go_product'))

    return render_template('manager_options/Product/update_product.html', options = options)


@app.route('/Product/delete_product', methods=['POST', 'GET'])
def delete_product():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    options = product.get_dropdown_products()
    if request.method == 'POST':
        product_id = request.form.get('product_name')
        print(product_id)
        comma_index = product_id.index(',')
        product_id = product_id[1:comma_index].strip()
        product_id = int(product_id)
        product.delete_product(product_id)
        return redirect(url_for('go_product'))

    return render_template('manager_options/Product/delete_product.html', options = options)

@app.route('/Product/report_products')
def report_products():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Отримати всі товари з бази даних
    products=product.get_all_products()

    # Передати дані товарів у шаблон і відобразити звіт
    return render_template('manager_options/Product/report_products.html', products=products)

@app.route('/Product/gryn_custom_1', methods=['GET', 'POST'])
def gryn_custom_1():
    cursor = conn.cursor()
    query = '''
        SELECT P.id_product, P.product_name
        FROM Product AS P
        WHERE P.id_product IN (
            SELECT SP.Id_product
            FROM Store_Product SP
            WHERE SP.UPC IN (
                SELECT S.UPC
                FROM Sale S
                GROUP BY S.UPC
                HAVING SUM(S.product_number) = (
                    SELECT MAX(subquery.total_bought)
                    FROM (
                        SELECT SUM(S2.product_number) AS total_bought
                        FROM Sale S2
                        GROUP BY S2.UPC
                    ) AS subquery
                )
            )
        );
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return render_template('manager_options/Product/query_gryn_1.html', data=results)

# #--------------------- PRODUCT_STORE

@app.route('/Product_Store/add_product_store', methods=['GET', 'POST'])
def add_product_store():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if request.method == 'POST':
        prom = request.form.get('promotional_product')
        if prom is None:
            prom = 0
        data = [
            request.form.get('UPC'),
            request.form.get('UPC_prom'),
            request.form.get('id_product'),
            request.form.get('selling_price'),
            request.form.get('products_number'),
            prom,
        ]
        print(data)  # Printing data for verification
        # Process the data and save it to the database
        store_product.insert_store_product(data)
        return redirect(url_for('go_product_store'))  # Redirect to the manager's cabinet page

    return render_template('manager_options/Product_Store/add_product_store.html')


@app.route('/Product_Store/update_product_store', methods=['GET', 'POST'])
def update_product_store():
    if not session.get("manager"):
        return redirect(url_for('home'))
    options = store_product.get_dropdown_product_store()
    if request.method == 'POST':
        Upc = request.form.get('UPC')
        Upc = Upc.strip('()')
        Upc = Upc.split(', ')
        Upc = Upc[0][1:-1]
        data = [
            Upc,
            request.form.get('UPC_prom'),
            request.form.get('id_product'),
            request.form.get('selling_price'),
            request.form.get('products_number'),
            request.form.get('promotional_product'),
        ]
        print(data)  # Printing data for verification
        # Process the data and save it to the database
        store_product.update_store_product(data)
        return redirect(url_for('go_product_store'))  # Redirect to the manager's cabinet page

    return render_template('manager_options/Product_Store/update_product_store.html', options = options)


@app.route('/Product_Store/delete_product_store', methods=['POST', 'GET'])
def delete_product_store():
    if not session.get("manager"):
        return redirect(url_for('home'))
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Перенаправлення на сторінку входу, якщо користувач не увійшов в систему
    options = store_product.get_dropdown_product_store()
    if request.method == 'POST':
        Upc = request.form.get('upc')
        Upc = Upc.strip('()')
        Upc = Upc.split(', ')
        Upc = Upc[0][1:-1]
        store_product.delete_store_product(Upc)
        return redirect(url_for('go_product_store'))

    return render_template('manager_options/Product_Store/delete_product_store.html', options = options)


@app.route('/Product_store/report_products_store')
def report_products_store():    #спільне для касира і менеджера
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Отримати всі товари в магазині з бази даних
    products=store_product.get_all_products()

    # Передати дані товарів у шаблон і відобразити звіт
    role = 0
    if session.get("manager"):
        role = 1
    return render_template('manager_options/Product_store/report_products_store.html', products=products, role=role)






#----------------------------------- ALL FOR CASHIER
@app.route('/cashier_cabinet', methods=['GET', 'POST'])
def cashier_cabinet():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not session.get("cashier"):
        return redirect(url_for('home'))
    options = customer_card.get_dropdown_customer_cards()


    if request.method == 'POST':
        card_number = request.form.get('card_number')
        card_number = card_number.strip('()')
        card_number = card_number.split(', ')
        card_number = card_number[0][1:-1]
        data = [
            request.form.get('check_number'),
            request.form.get('id_employee'),
           card_number,
            request.form.get('print_date'),
            request.form.get('upcs'),
            request.form.get('quantities')
        ]

       

        # Call insert_checkk() function to store data in the database
        checkk.insert_checkk(data)

    if request.method == 'POST':
        data = [
            request.form.get('check_number'),
            request.form.get('id_employee'),
            request.form.get('card_number'),
            request.form.get('print_date'),
            request.form.get('upcs'),
            request.form.get('quantities')
        ]

        # Call insert_checkk() function to store data in the database
        checkk.insert_checkk(data)

    id = session.get("id")
    data = employee.get_by_id(id)
    return render_template('cashier_cabinet.html', data=data, options = options)


@app.route('/all_products')
def all_products():
    id = session.get("id")
    data = employee.get_by_id(id)
    # Retrieve the list of products from your database
    products = product.get_all_products_sorted_by_name()  # Replace with your own function to fetch products


    return render_template('cashier_options/all_products.html', products=products, data = data)


@app.route('/all_products_store')
def all_products_store():
    id = session.get("id")
    data = employee.get_by_id(id)
    products=store_product.get_all_products_ordered_by_name()
    return render_template('cashier_options/all_products_store.html', products=products, data = data)


@app.route('/search_product_by_name', methods=['POST', 'GET'])
def search_product_by_name():
    id = session.get("id")
    data = employee.get_by_id(id)
    if request.method == 'POST':
        product_name = request.form['product_name']
        product=store_product.get_all_products_by_name(product_name)
        return render_template('cashier_options/product_by_name.html', product=product, data=data)
    product_name=""
    product = store_product.get_all_products_by_name(product_name)
    return render_template('cashier_options/product_by_name.html', product=product,data = data)




@app.route('/my_checks', methods=['POST', 'GET'])
def my_checks():
    id = session.get("id")
    data = employee.get_by_id(id)
    start_date=""
    end_date=""
    if request.form.get('start_date'):
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
    if request.form.get('end_date'):
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
    if not start_date:
       start_date="1900-01-01"
    if not end_date:
        end_date=date.today()

        # Виклик функції, яка повертає список чеків за вказаний проміжок часу
    checks = checkk.get_checks_by_cashier(session.get("id"),start_date, end_date)
    return render_template('cashier_options/my_checks.html', checks=checks, data=data)

@app.route('/me')
def me():
    id = session.get("id")
    data = employee.get_by_id(id)
    return render_template('cashier_options/me.html', data=data)


@app.route('/all_clients')
def all_clients():
    id = session.get("id")
    data = employee.get_by_id(id)
    clients = customer_card.get_all_clients_sorted_by_last_name()
    return render_template('cashier_options/all_clients.html', data=data, clients=clients)



if __name__ == '__main__':
    app.run(debug=True)





