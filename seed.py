from sqlite_db import get_db_connection

conn = get_db_connection()

cursor = conn.cursor()

# cursor.execute("""
#     INSERT INTO products
#     (category_number, manufacturer, product_name, characteristics)
#     VALUES (?, ?, ?, ?)
# """, (1, 'Coca-Cola Company', 'Coca-Cola', 'Carbonated soft drink, 0.5L bottle'))
#
# cursor.execute("""
#     INSERT INTO products
#     (category_number, manufacturer, product_name, characteristics)
#     VALUES (?, ?, ?, ?)
# """, (1, 'PepsiCo', 'Pepsi', 'Carbonated soft drink, 1L bottle'))
#
# cursor.execute("""
#     INSERT INTO products
#     (category_number, manufacturer, product_name, characteristics)
#     VALUES (?, ?, ?, ?)
# """, (2, 'Nestle', 'KitKat', 'Milk chocolate wafer bar, 41.5g'))

conn.commit()

conn.close()