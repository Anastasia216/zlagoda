from sqlite_db import get_db_connection

conn = get_db_connection()

cursor = conn.cursor()
#
# from uuid import uuid4
# from werkzeug.security import generate_password_hash
#
# # UUID для працівника
# manager_id = str(uuid4())
#
# # UUID для користувача
# user_id = str(uuid4())
#
# # Працівник
# conn.execute("""
# INSERT INTO employees(
#     id_employee,
#     empl_surname,
#     empl_name,
#     empl_patronymic,
#     empl_role,
#     salary,
#     date_of_birth,
#     date_of_start,
#     phone_number,
#     city,
#     street,
#     zip_code
# )
# VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# """, (
#     manager_id,
#     "Aydzar",
#     "Ivan",
#     "Petrovych",
#     "manager",
#     50000,
#     "1985-05-10",
#     "2020-01-01",
#     "+380671111111",
#     "Kyiv",
#     "Khreshchatyk",
#     "01001"
# ))
#
# # Користувач для входу
# conn.execute("""
# INSERT INTO users(
#     id_user,
#     id_employee,
#     username,
#     password_hash,
#     role
# )
# VALUES (?, ?, ?, ?, ?)
# """, (
#     user_id,
#     manager_id,
#     "manager",                    # логін
#     generate_password_hash("manager123"),  # пароль
#     "manager"
# ))
conn.commit()
conn.close()

print("Seed completed.")
