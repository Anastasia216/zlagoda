from sqlite_db import get_db_connection

def get_all_employees(search=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM employees '
                   'WHERE empl_surname LIKE ? '
                   '    OR empl_name LIKE ? '
                   'ORDER BY empl_surname ', (
        f"%{search}%",
        f"%{search}%",
    ))
    employees = cursor.fetchall()
    conn.close()
    return employees

def get_all_cashiers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM employees '
                   'WHERE empl_role = ? '
                   'ORDER BY empl_surname', ('cashier',))
    employees = cursor.fetchall()
    conn.close()
    return employees

def get_employee_by_id(id_employee):
    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute('SELECT * '
                   'FROM employees '
                   'WHERE id_employee = ?', (id_employee,))
    employee = cursor.fetchone()
    conn.close()
    return employee

def get_employee_by_surname(empl_surname):
    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute('SELECT * '
                   'FROM employees '
                   'WHERE empl_surname = ?', (empl_surname,))
    employee = cursor.fetchall()
    conn.close()
    return employee

def create_employee(data):
    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute('INSERT INTO employees '
                    '(id_employee, empl_surname, empl_name, empl_patronymic,'
                    ' empl_role, salary, date_of_birth, date_of_start, phone_number,'
                    ' city, street, zip_code)'
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
    (
        data['id_employee'],
        data['empl_surname'],
        data['empl_name'],
        data['empl_patronymic'],
        data['empl_role'],
        data['salary'],
        data['date_of_birth'],
        data['date_of_start'],
        data['phone_number'],
        data['city'],
        data['street'],
        data['zip_code']
    ))
    conn.commit()
    conn.close()

def update_employee(id_employee, data):
    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute('UPDATE employees '
                   'SET '
                   'empl_surname = ?, '
                   'empl_name = ?, '
                   'empl_patronymic = ?, '
                   'empl_role = ?, '
                   'salary = ?, '
                   'date_of_birth = ?, '
                   'date_of_start = ?, '
                   'phone_number = ?, '
                   'city = ?, '
                   'street = ?, '
                   'zip_code = ? '
                   'WHERE id_employee=?',
    (
        data['empl_surname'],
        data['empl_name'],
        data['empl_patronymic'],
        data['empl_role'],
        data['salary'],
        data['date_of_birth'],
        data['date_of_start'],
        data['phone_number'],
        data['city'],
        data['street'],
        data['zip_code'],
        id_employee,
    ))
    conn.commit()
    conn.close()

def delete_employee(id_employee):
    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute('DELETE FROM employees '
                   'WHERE id_employee = ?', (id_employee,))
    conn.commit()
    conn.close()



