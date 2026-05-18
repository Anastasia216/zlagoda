from sqlalchemy import CheckConstraint
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    ForeignKey,
    Boolean,
    VARCHAR,
    DECIMAL,
    Date,
    DateTime
)

from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    category_number = Column(Integer, primary_key=True)
    category_name = Column(VARCHAR(50), nullable=False)

class Product(Base):
    __tablename__ = "products"
    id_product = Column(Integer, primary_key=True)
    category_number = Column(Integer, ForeignKey('categories.category_number',onupdate='CASCADE',ondelete='NO ACTION'), nullable=False)
    manufacturer = Column(VARCHAR(50), nullable=False) #added due to text requirements
    product_name = Column(VARCHAR(50), nullable=False)
    characteristics = Column(VARCHAR(100), nullable=False)

class Store_Product(Base):
    __tablename__ = "store_products"
    UPC = Column(VARCHAR(12), primary_key=True)
    UPC_prom = Column(VARCHAR(12), ForeignKey('store_products.UPC', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    id_product = Column(Integer, ForeignKey('products.id_product', onupdate='CASCADE', ondelete='NO ACTION'), nullable=False)
    selling_price = Column(DECIMAL(13,4), nullable=False)
    products_number = Column(Integer, nullable=False)
    promotional_product = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        CheckConstraint('selling_price >= 0'),
        CheckConstraint('products_number >= 0')
    )


class Employee(Base):
    __tablename__ = "employees"
    id_employee = Column(VARCHAR(10), primary_key=True)
    empl_surname = Column(VARCHAR(50), nullable=False)
    empl_name = Column(VARCHAR(50), nullable=False)
    empl_patronymic = Column(VARCHAR(50), nullable=True)
    empl_role = Column(VARCHAR(10), nullable=False)
    salary = Column(DECIMAL(13,4), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    date_of_start = Column(Date, nullable=False)
    phone_number = Column(VARCHAR(13), nullable=False)
    city = Column(VARCHAR(50), nullable=False)
    street = Column(VARCHAR(50), nullable=False)
    zip_code = Column(VARCHAR(9), nullable=False)

    __table_args__ = (
         CheckConstraint('salary >= 0'),
         CheckConstraint('length(phone_number) <= 13')
    )

class Customer_Card(Base):
    __tablename__ = "customer_cards"
    card_number = Column(VARCHAR(13), primary_key=True)
    cust_surname = Column(VARCHAR(50), nullable=False)
    cust_name = Column(VARCHAR(50), nullable=False)
    cust_patronymic = Column(VARCHAR(50), nullable=True)
    phone_number = Column(VARCHAR(13), nullable=False)
    city = Column(VARCHAR(50), nullable=True)
    street = Column(VARCHAR(50), nullable=True)
    zip_code = Column(VARCHAR(9), nullable=True)
    percent = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('length(phone_number) <= 13'),
        CheckConstraint('percent >= 0 AND percent <=100')
    )


class Receipt(Base):
    __tablename__ = "receipts"
    check_number = Column(VARCHAR(10), primary_key=True)
    id_employee = Column(VARCHAR(10), ForeignKey('employees.id_employee',onupdate='CASCADE',ondelete='NO ACTION'), nullable=False)
    card_number = Column(VARCHAR(13), ForeignKey('customer_cards.card_number', onupdate='CASCADE',ondelete='NO ACTION'), nullable=True)
    print_date = Column(DateTime, nullable=False)
    sum_total = Column(DECIMAL(13,4), nullable=False)
    vat = Column(DECIMAL(13,4), nullable=False)


class Sale(Base):
    __tablename__ = "sales"
    UPC = Column(VARCHAR(12), ForeignKey('store_products.UPC', onupdate='CASCADE', ondelete='NO ACTION'), primary_key=True)
    check_number = Column(VARCHAR(10), ForeignKey('receipts.check_number', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    product_number = Column(Integer, nullable=False)
    selling_price = Column(DECIMAL(13,4), nullable=False)

    __table_args__ = (
        CheckConstraint('product_number >= 0'),
        CheckConstraint('selling_price >= 0')
    )