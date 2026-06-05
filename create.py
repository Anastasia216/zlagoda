from datetime import date

from app import create_app
from extensions import db
from database.models import Employee, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    employee = Employee(
        id_employee="EMP0000001",
        empl_surname="Admin",
        empl_name="System",
        empl_patronymic=None,
        empl_role="manager",
        salary=50000,
        date_of_birth=date(1990, 1, 1),
        date_of_start=date.today(),
        phone_number="380501111111",
        city="Kyiv",
        street="Admin Street",
        zip_code="01001"
    )

    db.session.add(employee)

    user = User(
        id_user="USR0000001",
        id_employee="EMP0000001",
        username="admin",
        password_hash=generate_password_hash("admin123"),
        role="manager"
    )

    db.session.add(user)

    db.session.commit()

    print("Manager created successfully")
    print("Login: admin")
    print("Password: admin123")