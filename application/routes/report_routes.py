from flask import Blueprint, render_template, request, abort
from sqlite_db import get_db_connection
from application.decorators import login_required, role_required
from datetime import datetime

report_routes = Blueprint("report_routes", __name__)

@report_routes.route("/<string:page_source>/report")
@login_required
@role_required("manager")
def generate_report(page_source):
    conn = get_db_connection()
    report_title = ""
    headers = []
    data = []

    if page_source == "employees":
        report_title = "All Employees Report"
        headers = ["ID", "Full Name", "Role", "Salary", "Phone", "Address", "Start Date"]
        rows = conn.execute("""
                            SELECT id_employee,
                                   empl_surname,
                                   empl_name,
                                   empl_patronymic,
                                   empl_role,
                                   salary,
                                   phone_number,
                                   city,
                                   street,
                                   zip_code,
                                   date_of_start
                            FROM employees -- <-- ТУТ БУЛО "employee", ДОДАЙ ЛІТЕРУ "s"!
                            ORDER BY empl_surname
                            """).fetchall()
        for r in rows:
            patr = r['empl_patronymic'] if r['empl_patronymic'] else ''
            addr = f"{r['zip_code'] or ''}, {r['city'] or ''}, {r['street'] or ''}".strip(", ")
            data.append([
                r['id_employee'],
                f"{r['empl_surname']} {r['empl_name']} {patr}",
                r['empl_role'].capitalize(),
                f"{r['salary']} ₴",
                r['phone_number'],
                addr if addr else "-",
                r['date_of_start']
            ])

    elif page_source == "customer_cards":
        report_title = "Permanent Customers Report"
        headers = ["Card ID", "Customer Full Name", "Phone Number", "Full Address", "Discount"]
        rows = conn.execute("""
                            SELECT card_number,
                                   cust_surname,
                                   cust_name,
                                   cust_patronymic,
                                   phone_number,
                                   city,
                                   street,
                                   zip_code,
                                   percent
                            FROM customer_cards
                            ORDER BY cust_surname
                            """).fetchall()
        for r in rows:
            patr = r['cust_patronymic'] if r['cust_patronymic'] else ''
            addr = f"{r['zip_code'] or ''}, {r['city'] or ''}, {r['street'] or ''}".strip(", ")
            data.append([
                r['card_number'],
                f"{r['cust_surname']} {r['cust_name']} {patr}",
                r['phone_number'],
                addr if addr else "-",
                f"{r['percent']}%"
            ])

    elif page_source == "categories":
        report_title = "Product Categories Report"
        headers = ["Category ID", "Category Name"]
        rows = conn.execute("SELECT category_number, category_name FROM categories ORDER BY category_name").fetchall()
        for r in rows:
            data.append([r['category_number'], r['category_name']])

    elif page_source == "products":
        report_title = "General Product Catalog Report"
        headers = ["ID", "Product Name", "Category", "Manufacturer", "Characteristics"]
        rows = conn.execute("""
                            SELECT p.id_product, p.product_name, c.category_name, p.manufacturer, p.characteristics
                            FROM products p
                                     JOIN categories c ON p.category_number = c.category_number
                            ORDER BY p.product_name
                            """).fetchall()
        for r in rows:
            data.append(
                [r['id_product'], r['product_name'], r['category_name'], r['manufacturer'], r['characteristics']])

    elif page_source == "store_products":
        report_title = "Products In Store Inventory Report"
        headers = ["UPC", "Promo UPC", "Product Name", "Manufacturer", "Price", "Qty in Store", "Is Promo"]
        rows = conn.execute("""
                            SELECT sp.UPC,
                                   sp.UPC_prom,
                                   sp.selling_price,
                                   sp.products_number,
                                   sp.promotional_product,
                                   p.product_name,
                                   p.manufacturer
                            FROM store_products sp
                                     JOIN products p ON sp.id_product = p.id_product
                            ORDER BY p.product_name
                            """).fetchall()
        for r in rows:
            data.append([
                r['UPC'],
                r['UPC_prom'] if r['UPC_prom'] else "-",
                r['product_name'],
                r['manufacturer'],
                f"{r['selling_price']} ₴",
                r['products_number'],
                "Yes" if r['promotional_product'] == 1 else "No"
            ])

    elif page_source in ["checks", "receipts"]:
        report_title = "Store Register Receipts Report"
        headers = ["Check Number", "Cashier ID", "Customer Card", "Print Date", "Total Sum", "VAT (20%)"]
        rows = conn.execute("""
                            SELECT check_number, id_employee, card_number, print_date, sum_total, vat
                            FROM receipts
                            ORDER BY print_date DESC
                            """).fetchall()
        for r in rows:
            data.append([
                r['check_number'],
                r['id_employee'],
                r['card_number'] if r['card_number'] else "Non-member",
                r['print_date'],
                f"{r['sum_total']} ₴",
                f"{r['vat']} ₴"
            ])
    else:
        conn.close()
        abort(404)

    conn.close()
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "reports/printable_report.html", report_title=report_title, headers=headers, data=data, generated_at=generated_at)