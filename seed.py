from sqlite_db import get_db_connection

conn = get_db_connection()

cursor = conn.cursor()

# conn.execute("""
# INSERT INTO store_products (
#     UPC,
#     UPC_prom,
#     id_product,
#     selling_price,
#     products_number,
#     promotional_product
# )
# VALUES (
#     '2',
#     NULL,
#     3,
#     4,
#     5,
#     6
# )
# """)
conn.commit()

conn.close()
