from sqlite3 import IntegrityError
from typing import Iterable

from employee import conn

def get_all_checks():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Checkk")
    checks = cursor.fetchall()
    cursor.close()
    return checks
def insert_checkk(check_data):
    """Insert a new check into the Checkk table and corresponding sales into the Sale table"""

    check_number, id_employee, card_number, print_date, upcs, quantities = check_data

    # Retrieve selling prices from Store_Product table
    # Check if the quantities are more than zero
    for quantity in quantities:
        if quantity <= 0:
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
        selling_price * quantity if selling_price is not None else 0
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
    percent = cursor.fetchone()[0]
    cursor.close()
    return float(percent)


""" 
TESTING CHECK INSERT, DELETE
"""


# check_data = (
#     "CHK0016",  # check_number
#     "EMP001",  # id_employee
#     None,  # card_number
#     "2023-06-08",  # print_date
#     [
#         "UPC001",  # upc
#         "UPC002",
#         "UPC003"
#     ],
#     [
#         2,  # quantity
#         1,
#         3
#     ]
# )
#
# insert_checkk(check_data)
# delete_checkk("CHK0015")





