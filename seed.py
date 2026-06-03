from app import create_app
from extensions import db
from database.models import User, Employee
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

with app.app_context():

    employee = Employee(
        id_employee="E001",
        empl_surname="Admin",
        empl_name="System",
        empl_patronymic=None,
        empl_role="manager",
        salary=10000,
        date_of_birth=date(2000, 1, 1),
        date_of_start=date.today(),
        phone_number="+380000000000",
        city="Kyiv",
        street="Main",
        zip_code="00000"
    )

    db.session.add(employee)
    db.session.commit()

    user = User(
        id_user="U001",
        id_employee="E001",
        username="admin",
        password_hash=generate_password_hash("admin123"),
        role="manager"
    )

    db.session.add(user)
    db.session.commit()

    print("Admin user created")