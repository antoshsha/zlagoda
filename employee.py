import sqlite3
import datetime
from sqlite3 import IntegrityError
from typing import Iterable

db_file_path = r'D:/Мої документи/2YearNaukma/Summer/zlagoda/ais.db'
#db_file_path=r'D:\ais\zlagoda\ais.db'
#db_file_path = "/Users/antonmarynych/PycharmProjects/zlagoda12/ais.db"

conn = sqlite3.connect(db_file_path, check_same_thread=False)


def insert_employee(employee_data: Iterable) -> None:
    """ INSERTING A NEW EMPLOYEE"""
    id_employee, empl_surname, empl_name,\
    empl_patronymic, empl_role, salary,\
    date_of_birth, date_of_start, phone_number,\
    city, street, zip_code = employee_data

    if not id_employee or not empl_surname or not empl_name \
            or not empl_role or not salary or not date_of_birth \
            or not date_of_start or not phone_number or not city \
            or not street or not zip_code:
        raise ValueError("Missing required employee data")

    # Checking if the workers are 18+
    today = datetime.date.today()
    age_limit = today - datetime.timedelta(days=365*18)
    dob = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date()

    if dob > age_limit:
        raise ValueError("Employee must be 18 years or older")

    # Checking if the salary is not negative
    if float(salary) < 0:
        raise ValueError("Salary can not be less than zero")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Employee (id_employee, empl_surname, "
            "empl_name, empl_patronymic, empl_role, salary, date_of_birth, "
            "date_of_start, phone_number, city, street, "
            "zip_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            employee_data
        )
        conn.commit()
        cursor.close()
        print("Employee data inserted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def update_employee(id_employee, updated_data):
    """Update employee information"""
    # Extract the updated data
    empl_surname, empl_name, empl_patronymic, \
    empl_role, salary, date_of_birth, \
    date_of_start, phone_number, \
    city, street, zip_code = updated_data

    # Perform data validation
    if not id_employee or not empl_surname or not empl_name \
            or not empl_role or not salary or not date_of_birth \
            or not date_of_start or not phone_number or not city \
            or not street or not zip_code:
        raise ValueError("Missing required employee data")

    today = datetime.date.today()
    age_limit = today - datetime.timedelta(days=365 * 18)
    dob = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date()

    if dob > age_limit:
        raise ValueError("Employee must be 18 years or older")

    if float(salary) < 0:
        raise ValueError("Salary cannot be less than zero")

    try:
        # Update data in the database
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Employee SET empl_surname=?, "
            "empl_name=?, empl_patronymic=?, empl_role=?, "
            "salary=?, date_of_birth=?, date_of_start=?, phone_number=?, "
            "city=?, street=?, zip_code=? WHERE id_employee=?",
            (*updated_data, id_employee)
        )
        conn.commit()
        cursor.close()
        print("Employee data updated successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))
        # Handle the constraint violation error here


def delete_employee(id_employee):
    """Delete an employee"""
    try:
        # Delete the employee from the database
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Employee WHERE id_employee=?", (id_employee,))
        conn.commit()
        cursor.close()
        print("Employee deleted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))
        # Handle the constraint violation error here

def get_all_employees():
    """Get all employees from the database"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employee")
        employees = cursor.fetchall()
        cursor.close()
        return employees
    except Exception as e:
        print("Error: Unable to fetch employees -", str(e))
        return []
    
def get_dropdown_employee():
    """Get all employees from the database"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_employee, empl_surname FROM Employee")
        employees = cursor.fetchall()
        cursor.close()
        return employees
    except Exception as e:
        print("Error: Unable to fetch employees -", str(e))
        return []


def get_all_employees_sorted_by_surname():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Employee ORDER BY empl_surname")
    employees = cursor.fetchall()
    cursor.close()
    return employees


def get_by_surname(surname):
    """Get phone number and address by surname"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number, city, street, zip_code FROM Employee WHERE empl_surname=?", (surname,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            phone_number, city, street, zip_code = result
            return phone_number, f"{city}, {street}, zip:{zip_code}"
        else:
            return None, None
    except Exception as e:
        print("Error: Unable to fetch employee by surname -", str(e))
        return None, None

def get_by_id(id):
    """Get phone number and address by surname"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employee WHERE id_employee=?", (id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result
        else:
            return None, None
    except Exception as e:
        print("Error: Unable to fetch employee by surname -", str(e))
        return None, None
""" 
TESTING UPDATING 
"""

# employee_id = 'E008'
# updated_employee_data = ('Man', 'Jane', 'Smith', 'Manager', 2100.00, '1990-01-01', '2015-01-01', '+987654321',
#                          'New City', 'New Street', '54321')
# update_employee(employee_id, updated_employee_data)


# employee_id = 'ID685493TEST'
# updated_employee_data = ['ni43ninf', 'ni43ninf', 'ni43ninf', 'Manager', '2982', '1999-03-20', '1999-03-20', '23242', 'fnwnfiewn', 'fwinfwf', '3242432']
# update_employee(employee_id, updated_employee_data)

"""
TESTING DELETION 
"""
# employee_id = 'E001'
# delete_employee(employee_id)


""" 
TESTING INSERTION 
"""


'''new_employee = (
    'E008', 'Doe', 'John', 'Smith', 'Manager', 5000.00, '2000-01-01', '2023-01-01',
   '+123456789', 'City', 'Street', '12345'
)
try:
    insert_employee(new_employee)
    print("Employee data inserted successfully.")
except ValueError as e:
    print("Error: Invalid employee data -", str(e))'''

