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

def get_dropdown_products():
    """Отримати всі товари з бази даних"""
    cursor = conn.cursor()
    cursor.execute("SELECT id_product, product_name FROM Product")
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


def info_by_name(product_name):
    cursor=conn.cursor()
    cursor.execute("SELECT sp.UPC, sp.UPC_prom, sp.id_product, sp.selling_price, sp.products_number, sp.promotional_product, p.category_number, p.product_name, p.characteristics FROM Store_Product AS sp JOIN Product AS p ON sp.id_product = p.id_product WHERE p.product_name LIKE ?",('%' + product_name + '%',))
    result=cursor.fetchall()
    cursor.close()
    return result

def get_all_products_sorted_by_name():
    cursor = conn.cursor()
    query = """
        SELECT id_product, category_number, product_name, characteristics
        FROM Product
        ORDER BY product_name
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results
"""TESTING INSERTING, UPDATING AND DELETING PRODUCTS"""

# product_data = (50, "Product GG", "Characteristics A")
# insert_product(product_data)

# product_data = ("Updated Product", "Updated Characteristics", 7)
# update_product(product_data)

# product_id = 4
# delete_product(product_id)
