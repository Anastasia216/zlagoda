from sqlite_db import get_db_connection


def get_all_customer_cards(search='', percent=''):
    conn = get_db_connection()
    cursor = conn.cursor()

    if search and percent:
        cursor.execute("""
                       SELECT *
                       FROM customer_cards
                       WHERE (
                           cust_surname LIKE ?
                               OR cust_name LIKE ?
                               OR card_number LIKE ?
                           )
                         AND percent = ?
                       ORDER BY cust_surname
                       """,
                       (
                           f"%{search}%",
                           f"%{search}%",
                           f"%{search}%",
                           percent
                       ))

    elif search:
        cursor.execute("""
                       SELECT *
                       FROM customer_cards
                       WHERE cust_surname LIKE ?
                          OR cust_name LIKE ?
                          OR card_number LIKE ?
                       ORDER BY cust_surname
                       """,
                       (
                           f"%{search}%",
                           f"%{search}%",
                           f"%{search}%"
                       ))

    elif percent:
        cursor.execute("""
                       SELECT *
                       FROM customer_cards
                       WHERE percent = ?
                       ORDER BY cust_surname
                       """,
                       (percent,))

    else:
        cursor.execute("""
                       SELECT *
                       FROM customer_cards
                       ORDER BY cust_surname
                       """)

    customer_cards = cursor.fetchall()
    conn.close()
    return customer_cards


def get_all_customer_cards_with_percent(percent):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT *
                   FROM customer_cards
                   WHERE percent = ?
                   ORDER BY cust_surname
                   """, (percent,))
    customer_cards = cursor.fetchall()
    conn.close()
    return customer_cards


def get_customer_card_by_number(card_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT *
                   FROM customer_cards
                   WHERE card_number = ?
                   """, (card_number,))
    customer_card = cursor.fetchone()
    conn.close()
    return customer_card


def create_customer_card(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO customer_cards
                   (card_number, cust_surname, cust_name, cust_patronymic,
                    phone_number, city, street, zip_code, percent)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   """,
                   (
                       data['card_number'].strip(),
                       data['cust_surname'].strip(),
                       data['cust_name'].strip(),
                       data.get('cust_patronymic', '').strip() or None,
                       data['phone_number'].strip(),
                       data.get('city', '').strip() or None,
                       data.get('street', '').strip() or None,
                       data.get('zip_code', '').strip() or None,
                       data['percent']
                   ))
    conn.commit()
    conn.close()


def update_customer_card(card_number, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE customer_cards
                   SET card_number     = ?,
                       cust_surname    = ?,
                       cust_name       = ?,
                       cust_patronymic = ?,
                       phone_number    = ?,
                       city            = ?,
                       street          = ?,
                       zip_code        = ?,
                       percent         = ?
                   WHERE card_number = ?
                   """,
                   (
                       data['card_number'].strip(),
                       data['cust_surname'].strip(),
                       data['cust_name'].strip(),
                       data.get('cust_patronymic', '').strip() or None,
                       data['phone_number'].strip(),
                       data.get('city', '').strip() or None,
                       data.get('street', '').strip() or None,
                       data.get('zip_code', '').strip() or None,
                       data['percent'],
                       card_number
                   ))
    conn.commit()
    conn.close()


def delete_customer_card(card_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   DELETE
                   FROM customer_cards
                   WHERE card_number = ?
                   """, (card_number,))
    conn.commit()
    conn.close()


def get_all_percents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT DISTINCT percent
                   FROM customer_cards
                   WHERE percent IS NOT NULL
                   ORDER BY percent
                   """)

    raw_percents = cursor.fetchall()
    conn.close()

    return [row['percent'] if hasattr(row, 'keys') else row[0] for row in raw_percents]


def get_customer_purchase_statistics(card_number, date_from, date_to):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(""" 
                    SELECT cc.card_number, cc.cust_surname, cc.cust_name,
                            COUNT(DISTINCT r.check_number) AS receipts_count,
                            SUM(s.product_number * s.selling_price) AS total_spent,
                            ROUND(SUM(s.product_number * s.selling_price) * 1.0 /COUNT(DISTINCT r.check_number), 2) AS average_receipt
                    FROM customer_cards cc
                    JOIN receipts r
                        ON cc.card_number = r.card_number
                    JOIN sales s
                        ON r.check_number = s.check_number
                    WHERE cc.card_number = ?
                      AND DATE(r.print_date) BETWEEN ? AND ?
                    GROUP BY cc.card_number, cc.cust_surname, cc.cust_name
    """, (card_number, date_from, date_to))
    stats = cursor.fetchone()
    conn.close()
    return stats

def is_universal_customer(card_number, date_from, date_to):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                SELECT NOT EXISTS (
                SELECT 1
                FROM categories c
                WHERE NOT EXISTS (  SELECT 1
                                    FROM receipts r
                                    JOIN sales s
                                        ON r.check_number = s.check_number
                                    JOIN store_products sp
                                        ON s.UPC = sp.UPC
                                    JOIN products p
                                        ON sp.id_product = p.id_product
                                    WHERE r.card_number = ?
                                      AND p.category_number = c.category_number
                                    AND DATE(r.print_date) BETWEEN ? AND ?  
                                    )
                ) AS universal_customer;
    """, (card_number, date_from, date_to))
    result = cursor.fetchone()
    conn.close()
    return bool(result["universal_customer"])