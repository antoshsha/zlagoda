from sqlite3 import IntegrityError
from employee import conn


def insert_product(product_data):
    """Insert a new product into the Product table"""
    try:
        cursor = conn.cursor()
        category_number, product_name, characteristics = product_data
        if not category_number or not product_name or not characteristics:
            raise ValueError("Missing required product data")

        if not validate_category(category_number):
            raise ValueError("Invalid category number")

        cursor.execute("INSERT INTO Product (category_number, product_name, characteristics) VALUES (?, ?, ?)",
                       product_data)
        conn.commit()
        cursor.close()
        print("Product data inserted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def update_product(product_data):
    """Update an existing product in the Product table"""
    try:
        cursor = conn.cursor()

        category_number, product_name, characteristics = product_data
        if not category_number or not product_name or not characteristics:
            raise ValueError("Missing required product data")

        cursor.execute("UPDATE Product SET product_name = ?, characteristics = ? WHERE id_product = ?",
                       product_data)
        conn.commit()
        cursor.close()
        print("Product data updated successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def delete_product(product_id):
    """Delete a product from the Product table"""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Product WHERE id_product = ?", (product_id,))
        conn.commit()
        cursor.close()
        print("Product deleted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def get_all_products():
    """Отримати всі товари з бази даних"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    cursor.close()
    return products


def validate_category(category_number):

    """Check if a category with the given category_number exists in the Category table"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Category WHERE category_number = ?", (category_number,))
    result = cursor.fetchone()[0]
    cursor.close()
    return result > 0


"""TESTING INSERTING, UPDATING AND DELETING PRODUCTS"""

# product_data = (20, "Product A", "Characteristics A")
# insert_product(product_data)

# product_data = ("Updated Product", "Updated Characteristics", 1)
# update_product(product_data)

# product_id = 4
# delete_product(product_id)