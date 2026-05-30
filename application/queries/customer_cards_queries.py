from sqlite_db import get_db_connection

def get_all_customer_cards(search =''):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute( 'SELECT * '
                    'FROM customer_cards '
                    'WHERE cust_surname LIKE ? '
                    'OR cust_name LIKE ? '
                    'ORDER BY cust_surname',
                    (
                          f'%{search}%',
                          f'%{search}%'
                    )
                )
    customer_cards = cursor.fetchall()
    conn.close()
    return customer_cards

def get_all_customer_cards_with_percent(percent):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM customer_cards '
                   'WHERE percent = ? '
                   'ORDER BY cust_surname', (percent,))
    customer_cards = cursor.fetchall()
    conn.close()
    return customer_cards

def get_customer_card_by_number(card_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM customer_cards '
                   'WHERE card_number = ?', (card_number,))
    customer_card = cursor.fetchone()
    conn.close()
    return customer_card

def create_customer_card(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO customer_cards '
                   '(card_number, cust_surname, cust_name, cust_patronymic, '
                   'phone_number, city, street, zip_code, percent ) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (
                       data['card_number'],
                       data['cust_surname'],
                       data['cust_name'],
                       data['cust_patronymic'],
                       data['phone_number'],
                       data['city'],
                       data['street'],
                       data['zip_code'],
                       data['percent']
                   ))
    conn.commit()
    conn.close()

def update_customer_card(card_number, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE customer_cards '
                   'SET '
                   'card_number = ?, '
                   'cust_surname = ?, '
                   'cust_name = ?, '
                   'cust_patronymic = ?, '
                   'phone_number = ?, '
                   'city = ?, '
                   'street = ?, '
                   'zip_code = ?, '
                   'percent = ? '
                   'WHERE card_number = ?',
                   (
                       data['card_number'],
                       data['cust_surname'],
                       data['cust_name'],
                       data['cust_patronymic'],
                       data['phone_number'],
                       data['city'],
                       data['street'],
                       data['zip_code'],
                       data['percent'],
                       card_number
                   ))
    conn.commit()
    conn.close()

def delete_customer_card(card_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM customer_cards '
                   'WHERE card_number = ?', (card_number,))
    conn.commit()
    conn.close()