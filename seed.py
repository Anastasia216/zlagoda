from sqlite_db import get_db_connection

conn = get_db_connection()

cursor = conn.cursor()

cursor.execute("""
    INSERT INTO categories
    (category_number, category_name)
    VALUES (?, ?)
""", (2, 'Food'))

conn.commit()

conn.close()