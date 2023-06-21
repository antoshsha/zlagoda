from sqlite3 import IntegrityError
from typing import Iterable
import numpy as np
from employee import conn

def get_all_checks():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Checkk")
    checks = cursor.fetchall()
    cursor.close()
    return checks

def get_dropdown_checks():
    cursor = conn.cursor()
    cursor.execute("SELECT check_number FROM Checkk")
    checks = cursor.fetchall()
    cursor.close()
    return checks


def get_checks_by_cashier(cashier_id, start_date, end_date):
    cursor = conn.cursor()
    print("id"+str(cashier_id))
    if cashier_id:
        query = """
            SELECT c.check_number, c.id_employee, c.card_number, c.print_date, c.sum_total, c.vat, p.product_name, s.product_number, s.selling_price
            FROM Checkk AS c
            INNER JOIN Sale AS s ON c.check_number = s.check_number
            INNER JOIN Store_Product AS sp ON s.UPC = sp.UPC
            INNER JOIN Product AS p ON sp.id_product=p.id_product
            WHERE c.id_employee = ? AND c.print_date BETWEEN ? AND ?
        """
        params = (cashier_id, start_date, end_date)
    else:
        print("no_id")
        query = """
            SELECT c.check_number, c.id_employee, c.card_number, c.print_date, c.sum_total, c.vat, p.product_name, s.product_number, s.selling_price
            FROM Checkk AS c
            INNER JOIN Sale AS s ON c.check_number = s.check_number
            INNER JOIN Store_Product AS sp ON s.UPC = sp.UPC
            INNER JOIN Product AS p ON sp.id_product=p.id_product
            WHERE c.print_date BETWEEN ? AND ?
        """
        params = (start_date, end_date)

    cursor.execute(query, params)
    # Отримання результатів запиту
    results = cursor.fetchall()
    print("res:"+str(results))
    results=np.asarray(results)
    prev=["","","","",""]
    for check in results:
        if [check[0],check[1],check[2],check[3]]==prev:
            print(str([check[0],check[1],check[2],check[3]])+"=="+str(prev))
            for i in range(6):
                check[i]=""
        else:
            prev=[check[0],check[1],check[2],check[3]]
    print("----------------")
    print(results)
    cursor.close()
    return results


def insert_checkk(check_data):
    """Insert a new check into the Checkk table and corresponding sales into the Sale table"""

    check_number, id_employee, card_number, print_date, upcs, quantities = check_data
    upcs=upcs.split(" ")
    quantities=quantities.split(" ")
    # Retrieve selling prices from Store_Product table
    # Check if the quantities are more than zero
    for quantity in quantities:
        if float(quantity) <= 0:
            raise ValueError("Quantity must be more than zero")
    cursor = conn.cursor()
    selling_prices = []
    for upc in upcs:
        cursor.execute("SELECT selling_price FROM Store_Product WHERE UPC = ?", (upc,))
        result = cursor.fetchone()
        if result:
            selling_prices.append(result[0])
        else:
            selling_prices.append(None)
    cursor.close()

    # Insert sales into Sale table
    try:
        cursor = conn.cursor()
        for upc, quantity, selling_price in zip(upcs, quantities, selling_prices):
            cursor.execute(
                "INSERT INTO Sale (UPC, check_number, product_number, selling_price) "
                "VALUES (?, ?, ?, ?)",
                (upc, check_number, quantity, selling_price)
            )
        conn.commit()
        cursor.close()
        print("Sales data inserted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))

    # Calculate total sum
    total_sum = sum(
        float(selling_price) * float(quantity) if selling_price is not None else 0
        for selling_price, quantity in zip(selling_prices, quantities)
    )

    # Calculate total sum with the discount card
    if card_number is not None:
        card_percent = get_card_percent(card_number)
        total_sum -= (total_sum*card_percent)/100
    # Insert check into Checkk table
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Checkk (check_number, id_employee, card_number, print_date, sum_total) "
            "VALUES (?, ?, ?, ?, ?)",
            (check_number, id_employee, card_number, print_date, total_sum)
        )
        conn.commit()
        cursor.close()
        print("Check data inserted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))



def delete_checkk(check_number: str) -> None:
    """Delete a check and its corresponding sale items from the database"""
    cursor = conn.cursor()

    # Delete sale items associated with the check from the Sale table
    cursor.execute("DELETE FROM Sale WHERE check_number = ?", (check_number,))

    # Delete the check from the Checkk table
    cursor.execute("DELETE FROM Checkk WHERE check_number = ?", (check_number,))
    conn.commit()
    cursor.close()

    print("Check deleted successfully.")


def get_card_percent(card_number: str) -> float:
    """Retrieve the percent value associated with a customer card"""
    cursor = conn.cursor()
    cursor.execute("SELECT percent FROM Customer_Card WHERE card_number = ?", (card_number,))
    percent = 0
    if cursor is not None:
        percent = cursor.fetchone()
    if percent is None:
        return 0
    cursor.close()
    print(percent)
    return float(percent[0])


""" 
TESTING CHECK INSERT, DELETE
"""


# check_data = (
#     "CHK00109",  # check_number
#     "EMP001",  # id_employee
#     None,  # card_number
#     "2023-06-08",  # print_date
#     [
#         "UPC001",  # upc
#         "UPC002"
#
#     ],
#     [
#         2,  # quantity
#         1
#
#     ]
# )
#
# insert_checkk(check_data)
# delete_checkk("CHK0015")





