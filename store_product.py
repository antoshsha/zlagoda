from sqlite3 import IntegrityError
from typing import Iterable

from employee import conn

def get_all_products_ordered_by_name():
    cursor = conn.cursor()
    cursor.execute("""SELECT sp.UPC, sp.UPC_prom, p.id_product, p.category_number, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
FROM Store_Product sp
INNER JOIN Product p ON sp.id_product = p.id_product
ORDER BY p.product_name;""")
    products = cursor.fetchall()
    cursor.close()
    return products

def get_dropdown_product_store():
    cursor = conn.cursor()
    cursor.execute("""SELECT sp.UPC, p.product_name
                      FROM Store_Product sp
                      INNER JOIN Product p ON sp.id_product = p.id_product
                      ORDER BY sp.UPC;""")
    products = cursor.fetchall()
    cursor.close()
    return products
def insert_store_product(store_product_data):
    """Insert a new store product or update an existing one"""
    UPC, UPC_prom, id_product, selling_price, products_number, promotional_product = store_product_data
    if float(selling_price) < 0:
        raise ValueError("Selling price can not be less than zero")
    if float(products_number) < 0:
        raise ValueError("The number of products can not be less than zero")
    if promotional_product:
        # Check if the promotional product already exists in the table
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Store_Product WHERE UPC = ?", (UPC,))
        result = cursor.fetchone()[0]
        cursor.close()

        if float(result) > 0:
            print("Error: Promotional product already exists in the table.")
            return

        if UPC_prom:
            # Retrieve the selling_price of the promotional product
            cursor = conn.cursor()
            cursor.execute("SELECT selling_price FROM Store_Product WHERE UPC = ?", (UPC_prom,))
            try:
                promoted_selling_price = cursor.fetchone()[0]
                cursor.close()
                # Calculate the new selling_price as 0.8 times the promoted selling_price
                selling_price = 0.8 * promoted_selling_price
            except TypeError as e:
                print("You have to insert the non-promotional product first")
                return
        else:
            print("Error: Promotional product must have a foreign key.")
            return

    # Check if a non-promotional store product with the same id_product already exists
    if not promotional_product:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT UPC, products_number, selling_price FROM Store_Product "
            "WHERE id_product = ? AND promotional_product = 0", (id_product,)
        )
        existing_product = cursor.fetchone()

        if existing_product:
            existing_UPC, existing_products_number, existing_selling_price = existing_product

            # Increment the products_number and update the selling_price
            new_products_number = existing_products_number + products_number
            new_selling_price = selling_price

            # Update the existing store product
            cursor.execute(
                "UPDATE Store_Product SET products_number = ?, selling_price = ? "
                "WHERE UPC = ?", (new_products_number, new_selling_price, existing_UPC)
            )
            conn.commit()
            cursor.close()
            print("Store product updated successfully.")
            return

    # Insert a new store product
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Store_Product (UPC, UPC_prom, id_product, selling_price, "
        "products_number, promotional_product) VALUES (?, ?, ?, ?, ?, ?)",
        (store_product_data[0], store_product_data[1], store_product_data[2],
         selling_price, store_product_data[4], store_product_data[5])
    )
    conn.commit()
    cursor.close()
    print("Store product inserted successfully.")


def update_store_product(store_product_data):
    """Update an existing store product"""
    UPC, UPC_prom, id_product, selling_price, products_number, promotional_product = store_product_data

    # Validate data
    if float(selling_price) < 0 or float(products_number) < 0:
        raise ValueError("Price and products number must be greater than or equal to zero")

    if promotional_product:
        # Check if the promotional product UPC exists
        if not validate_store_product(UPC_prom):
            raise ValueError("Invalid UPC for the promotional product")

        # Get the selling price of the promotional product
        cursor = conn.cursor()
        cursor.execute("SELECT selling_price FROM Store_Product WHERE UPC = ?", (UPC_prom,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            selling_price = result[0] * 0.8

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Store_Product SET UPC_prom = ?, id_product = ?, selling_price = ?, products_number = ?, "
            "promotional_product = ? WHERE UPC = ?",
            (UPC_prom, id_product, selling_price, products_number, promotional_product, UPC)
        )
        conn.commit()
        cursor.close()
        print("Store product data updated successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def delete_store_product(UPC):
    """Delete an existing store product"""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Store_Product WHERE UPC = ?", (UPC,))
        conn.commit()
        cursor.close()
        print("Store product data deleted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))

def get_all_products_by_name(product_name):
    cursor = conn.cursor()
    if product_name == "":
        # Запит до бази даних для отримання всіх товарів
        cursor.execute(
            "SELECT * FROM Store_Product AS sp INNER JOIN Product AS p ON sp.id_product = p.id_product")
    else:
        # Запит до бази даних для пошуку товару за назвою
        cursor.execute(
            "SELECT * FROM Store_Product AS sp INNER JOIN Product AS p ON sp.id_product = p.id_product WHERE p.product_name LIKE ?",
            ('%' + product_name + '%',))

    products = cursor.fetchall()
    cursor.close()
    return products

def get_all_products():
    cursor = conn.cursor()
    cursor.execute("""SELECT *
    FROM Store_Product""")
    products = cursor.fetchall()
    cursor.close()
    return products
def validate_store_product(UPC):
    """Check if a store product with the given UPC exists in the Store_Product table"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Store_Product WHERE UPC = ?", (UPC,))
    result = cursor.fetchone()
    cursor.close()
    return float(result[0]) > 0


"""TESTING """



# store_product_data1 = ("UPC006", "UPC005", 16, 10, 60, True)
# insert_store_product(store_product_data1)


# store_product_data = ("UPC013", "UPC012", 5, -20, 45, True)
# insert_store_product(store_product_data)

# delete_store_product("UPC012")
#
# update_store_product(store_product_data1)