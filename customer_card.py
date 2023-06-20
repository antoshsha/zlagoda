from sqlite3 import IntegrityError
from typing import Iterable

from employee import conn


def insert_customer_card(card_data: Iterable) -> None:
    """Insert a new customer card into the Customer_Card table"""

    try:
        card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent = card_data
        if float(percent) < 0:
            raise ValueError("Percent can not be less than zero")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Customer_Card (card_number, cust_surname, cust_name, cust_patronymic, phone_number, "
            "city, street, zip_code, percent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            card_data
        )
        conn.commit()
        cursor.close()
        print("Customer card data inserted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def update_customer_card(updated_data: Iterable) -> None:
    """Update the information of an existing customer card"""
    try:
        card_number = updated_data[0]
        if not validate_customer_card(card_number):
            raise ValueError("Invalid customer card number")

        if float(updated_data[-1]) < 0:
            raise ValueError("Percent can not be less than zero")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Customer_Card SET cust_surname = ?, cust_name = ?, cust_patronymic = ?, "
            "phone_number = ?, city = ?, street = ?, zip_code = ?, percent = ? "
            "WHERE card_number = ?",
            (*updated_data[1:], card_number)
        )
        conn.commit()
        cursor.close()
        print("Customer card data updated successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def delete_customer_card(card_number: str) -> None:
    """Delete an existing customer card"""
    if not validate_customer_card(card_number):
        raise ValueError("Invalid customer card number")

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Customer_Card WHERE card_number = ?", (card_number,))
        conn.commit()
        cursor.close()
        print("Customer card data deleted successfully.")
    except IntegrityError as e:
        print("Error: Database constraint violation -", str(e))


def validate_customer_card(card_number: str) -> bool:
    """Check if a customer card with the given card number exists in the Customer_Card table"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Customer_Card WHERE card_number = ?", (card_number,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] > 0


def get_all_customer_cards():
    """Get information of all customer cards"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Customer_Card")
        cards = cursor.fetchall()
        cursor.close()
        return cards
    except Exception as e:
        print("Error: Failed to retrieve customer card data -", str(e))
        return []
    
def get_dropdown_customer_cards():
    """Get information of all customer cards"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT card_number, cust_surname FROM Customer_Card")
        cards = cursor.fetchall()
        cursor.close()
        return cards
    except Exception as e:
        print("Error: Failed to retrieve customer card data -", str(e))
        return []


def get_cards_by_discount(discount):
    """Get customer cards with the given discount percentage"""

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Customer_Card WHERE percent = ?", (discount,))
        cards = cursor.fetchall()
        cursor.close()
        return cards
    except Exception as e:
        print("Error: Failed to retrieve customer card data -", str(e))
        return []


def get_all_clients_sorted_by_last_name():
    query = "SELECT * FROM Customer_card ORDER BY cust_surname"
    cursor = conn.cursor()
    cursor.execute(query)
    result =cursor.fetchall()
    cursor.close()
    return result
"""
TESTING INSERTION, DELETING AND UPDATING IN CUSTOM_CARD
"""

# try:
#     # card_data = ("CARD006", "Smith", "John", "", "+987654321", "London", "Street 2", "12345", 5)
#     # insert_customer_card(card_data)
#
#
#     # card_data = ("CARD006", "Smith", "Jenna", "", "+987654321", "London", "Street 2", "12345", 10)
#     # update_customer_card(card_data)
#
#
#     # card_number = "CARD006"
#     # delete_customer_card(card_number)
#
# except ValueError as s:
#     print(e)