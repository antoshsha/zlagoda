from sqlite3 import IntegrityError
from employee import conn


def insert_category(category_data):
    """Insert a new category"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Category (category_name) VALUES (?)",
            (category_data,)
        )
        conn.commit()
        cursor.close()
        print("Category inserted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def update_category(category_number, category_name):
    print(category_number)
    try:
        cursor = conn.cursor()
        result = cursor.execute("UPDATE Category SET category_name = ? WHERE category_number = ?",
                                (category_name, category_number))
        conn.commit()

        if result.rowcount == 0:
            print("No category found with category number", category_number)
        else:
            print("Category updated successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def delete_category(category_number):
    try:
        cursor = conn.cursor()
        result = cursor.execute("DELETE FROM Category WHERE category_number = ?", (category_number,))
        conn.commit()
        print(category_number)
        if result.rowcount == 0:
            print("No category found with category number", category_number)
        else:
            print("Category deleted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def get_all_categories():
    """Get information of all categories"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Category")
        categories = cursor.fetchall()
        cursor.close()
        return categories
    except Exception as e:
        print("Error: Failed to retrieve category data -", str(e))
        return []
    

"""
TESTING DELETING UPDATING AND INSERTING A CATEGORY
"""

# insert_category("test")
# update_category(5, "Electronics and Gadgets")
# delete_category(5)

