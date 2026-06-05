from app import create_app
from extensions import db
from database.models import Employee, User
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

with app.app_context():
    existing = User.query.filter_by(username="cashier").first()

    if existing:
        print("Cashier already exists")
    else:
        ...
    employee = Employee(
        id_employee="E002",
        empl_surname="Cashier",
        empl_name="Test",
        empl_patronymic=None,
        empl_role="cashier",
        salary=8000,
        date_of_birth=date(2000, 5, 5),
        date_of_start=date.today(),
        phone_number="+380111111111",
        city="Kyiv",
        street="Central",
        zip_code="01001"
    )

    db.session.add(employee)

    user = User(
        id_user="U002",
        id_employee="E002",
        username="cashier",
        password_hash=generate_password_hash("cashier123"),
        role="cashier"
    )

    db.session.add(user)

    db.session.commit()

    print("Cashier created")