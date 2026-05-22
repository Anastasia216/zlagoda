from extensions import db
from sqlalchemy import CheckConstraint, ForeignKey


class Category(db.Model):
    __tablename__ = 'categories'
    category_number = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.VARCHAR(50), nullable=False)

class Product(db.Model):
    __tablename__ = "products"
    id_product = db.Column(db.Integer, primary_key=True)
    category_number = db.Column(db.Integer, db.ForeignKey('categories.category_number',onupdate='CASCADE',ondelete='NO ACTION'), nullable=False)
    manufacturer = db.Column(db.VARCHAR(50), nullable=False) #added due to text requirements
    product_name = db.Column(db.VARCHAR(50), nullable=False)
    characteristics = db.Column(db.VARCHAR(100), nullable=False)

class Store_Product(db.Model):
    __tablename__ = "store_products"
    UPC = db.Column(db.VARCHAR(12), primary_key=True)
    UPC_prom = db.Column(db.VARCHAR(12), db.ForeignKey('store_products.UPC', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    id_product = db.Column(db.Integer, db.ForeignKey('products.id_product', onupdate='CASCADE', ondelete='NO ACTION'), nullable=False)
    selling_price = db.Column(db.DECIMAL(13,4), nullable=False)
    products_number = db.Column(db.Integer, nullable=False)
    promotional_product = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        db.UniqueConstraint(
            'UPC_prom',
            name='uq_store_products_upc_prom'
        ),
        CheckConstraint('selling_price >= 0'),
        CheckConstraint('products_number >= 0')
    )


class Employee(db.Model):
    __tablename__ = "employees"
    id_employee = db.Column(db.VARCHAR(10), primary_key=True)
    empl_surname = db.Column(db.VARCHAR(50), nullable=False)
    empl_name = db.Column(db.VARCHAR(50), nullable=False)
    empl_patronymic = db.Column(db.VARCHAR(50), nullable=True)
    empl_role = db.Column(db.VARCHAR(10), nullable=False)
    salary = db.Column(db.DECIMAL(13,4), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    date_of_start = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.VARCHAR(13), nullable=False)
    city = db.Column(db.VARCHAR(50), nullable=False)
    street = db.Column(db.VARCHAR(50), nullable=False)
    zip_code = db.Column(db.VARCHAR(9), nullable=False)

    __table_args__ = (
         CheckConstraint('salary >= 0'),
         CheckConstraint('length(phone_number) <= 13')
    )

class Customer_Card(db.Model):
    __tablename__ = "customer_cards"
    card_number = db.Column(db.VARCHAR(13), primary_key=True)
    cust_surname = db.Column(db.VARCHAR(50), nullable=False)
    cust_name = db.Column(db.VARCHAR(50), nullable=False)
    cust_patronymic = db.Column(db.VARCHAR(50), nullable=True)
    phone_number = db.Column(db.VARCHAR(13), nullable=False)
    city = db.Column(db.VARCHAR(50), nullable=True)
    street = db.Column(db.VARCHAR(50), nullable=True)
    zip_code = db.Column(db.VARCHAR(9), nullable=True)
    percent = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('length(phone_number) <= 13'),
        CheckConstraint('percent >= 0 AND percent <=100')
    )


class Receipt(db.Model):
    __tablename__ = "receipts"
    check_number = db.Column(db.VARCHAR(10), primary_key=True)
    id_employee = db.Column(db.VARCHAR(10), db.ForeignKey('employees.id_employee',onupdate='CASCADE',ondelete='NO ACTION'), nullable=False)
    card_number = db.Column(db.VARCHAR(13), db.ForeignKey('customer_cards.card_number', onupdate='CASCADE',ondelete='NO ACTION'), nullable=True)
    print_date = db.Column(db.DateTime, nullable=False)
    sum_total = db.Column(db.DECIMAL(13,4), nullable=False)
    vat = db.Column(db.DECIMAL(13,4), nullable=False)


class Sale(db.Model):
    __tablename__ = "sales"
    UPC = db.Column(db.VARCHAR(12), db.ForeignKey('store_products.UPC', onupdate='CASCADE', ondelete='NO ACTION'), primary_key=True)
    check_number = db.Column(db.VARCHAR(10), db.ForeignKey('receipts.check_number', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    product_number = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.DECIMAL(13,4), nullable=False)

    __table_args__ = (
        CheckConstraint('product_number >= 0'),
        CheckConstraint('selling_price >= 0')
    )
class User(db.Model):
    __tablename__ = "users"
    id_user = db.Column(db.VARCHAR(10), primary_key=True)
    id_employee = db.Column(db.VARCHAR(10), db.ForeignKey('employees.id_employee', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    username = db.Column(db.VARCHAR(50), nullable=False, unique=True)
    password_hash = db.Column(db.VARCHAR(255), nullable=False)
    role = db.Column(db.VARCHAR(10), nullable=False)