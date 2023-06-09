import sqlite3
import datetime
from sqlite3 import IntegrityError
from typing import Iterable

conn = sqlite3.connect('ais.db')


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
    if salary < 0:
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

    if salary < 0:
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


""" 
TESTING UPDATING 
"""
#
# employee_id = 'E001'
# updated_employee_data = ('Doe', 'Jane', 'Smith', 'Manager', 2100.00, '1990-01-01', '2015-01-01', '+987654321',
#                          'New City', 'New Street', '54321')
# update_employee(employee_id, updated_employee_data)


"""
TESTING DELETION 
"""
# employee_id = 'E001'
# delete_employee(employee_id)


""" 
TESTING INSERTION 
"""

#
# new_employee = (
#     'E002', 'Doe', 'John', 'Smith', 'Manager', 5000.00, '2000-01-01', '2023-01-01',
#     '+123456789', 'City', 'Street', '12345'
# )
#
# try:
#     insert_employee(new_employee)
#     print("Employee data inserted successfully.")
# except ValueError as e:
#     print("Error: Invalid employee data -", str(e))
