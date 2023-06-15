from sqlite3 import IntegrityError

from employee import conn


def insert_user(login, password, id_employee):
    """Insert a new user record"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO User (login, password, id_employee) VALUES (?, ?, ?)",
            (login, password, id_employee)
        )
        conn.commit()
        cursor.close()
        print("User inserted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))

def update_user(login, password, id_employee):
    """Update an existing user record"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE User SET password = ?, id_employee = ? WHERE login = ?",
            (password, id_employee, login)
        )
        conn.commit()
        cursor.close()
        print("User updated successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))

def delete_user(login):
    """Delete a user record"""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User WHERE login = ?", (login,))
        conn.commit()
        cursor.close()
        print("User deleted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))



# insert_user("johnsmith", "password123", "E008")
# update_user("johnsmith", "newpassword456", "E008")
delete_user("johnsmith")
