import uuid

from flask import Blueprint, Flask, render_template, request, redirect, url_for, jsonify
from sqlite_db import get_db_connection
import json
receipt_routes = Blueprint("receipt_routes", __name__)

@receipt_routes.route("/receipts")
def receipts():
    search = request.args.get("search", "").strip()
    conn = get_db_connection()
    if search:
        receipts = conn.execute("""SELECT r.check_number,
                                          r.print_date,
                                          r.sum_total,
                                          r.vat,
                                          
                                          e.empl_surname,
                                          e.empl_name,
                                          
                                          c.card_number,
                                          c.cust_surname,
                                          c.cust_name
                                   FROM receipts r
                                            JOIN employees e
                                                 ON r.id_employee = e.id_employee
                                            LEFT JOIN customer_cards c
                                                      ON r.card_number = c.card_number
                                            WHERE r.check_number LIKE ?
                                            OR e.empl_surname LIKE ?
                                            OR e.empl_name LIKE ?
                                            OR c.cust_surname LIKE ?
                                            OR c.cust_name LIKE ?
    
                                            ORDER BY r.print_date DESC
                                            """, (
                                            f"%{search}%",
                                            f"%{search}%",
                                            f"%{search}%",
                                            f"%{search}%",
                                            f"%{search}%"
                                            )).fetchall()
    else:
        receipts = conn.execute("""
                SELECT r.check_number,
                       r.print_date,
                       r.sum_total,
                       r.vat,

                       e.empl_surname,
                       e.empl_name,

                       c.card_number,
                       c.cust_surname,
                       c.cust_name

                FROM receipts r

                JOIN employees e
                     ON r.id_employee = e.id_employee

                LEFT JOIN customer_cards c
                     ON r.card_number = c.card_number

                ORDER BY r.print_date DESC
            """).fetchall()
    employees = conn.execute("""
            SELECT *
            FROM employees
            WHERE empl_role = 'Cashier'
            ORDER BY empl_surname
        """).fetchall()

    customer_cards = conn.execute("""
            SELECT *
            FROM customer_cards
            ORDER BY cust_surname
        """).fetchall()
    products = conn.execute("""
        SELECT sp.UPC,
               p.product_name
        FROM store_products sp
        JOIN products p
             ON p.id_product = sp.id_product
        ORDER BY p.product_name
    """).fetchall()

    conn.close()

    return render_template("receipts/receipts.html", receipts=receipts,products=products, employees=employees, customer_cards=customer_cards, search=search)


@receipt_routes.route("/receipts/add", methods=["GET", "POST"])
def add_receipt():
    conn = get_db_connection()
    search = request.args.get("search", "").strip()
    employees = conn.execute("""SELECT *
                                FROM employees
                                WHERE empl_role = 'Cashier'
                                ORDER BY empl_surname""").fetchall()

    customer_cards = conn.execute("""SELECT *
                                     FROM customer_cards
                                     ORDER BY cust_surname""").fetchall()
    if request.method == "POST":
        check_number = str(uuid.uuid4())[:10]
        id_employee = request.form["id_employee"]
        card_number = request.form.get("card_number")
        print_date = request.form["print_date"]

        products = json.loads(
            request.form["products"]
        )

        sum_total = 0

        for product in products:
            quantity = int(product["quantity"])
            price = float(product["price"])

            sum_total += quantity * price

        vat = round(sum_total * 0.20, 2)
        conn.execute("""INSERT INTO receipts (check_number,
                                              id_employee,
                                              card_number,
                                              print_date,
                                              sum_total,
                                              vat)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (check_number, id_employee, card_number if card_number else None, print_date, sum_total, vat))
        products = json.loads(
        request.form["products"]
    )
        for product in products:
            upc = product["upc"]
            quantity = int(product["quantity"])
            price = float(product["price"])

            conn.execute("""
                INSERT INTO sales(
                    UPC,
                    check_number,
                    product_number,
                    selling_price
                )
                VALUES (?, ?, ?, ?)
            """,
                         (
                             upc,
                             check_number,
                             quantity,
                             price
                         ))

        conn.commit()
        conn.close()
        return jsonify({
            "success": True
        })

@receipt_routes.route("/receipts/edit/<string:check_number>", methods=["GET", "POST"])
def edit_receipt(check_number):
    conn = get_db_connection()
    receipt = conn.execute("""SELECT *
                              FROM receipts
                              WHERE check_number = ?""", (check_number,)).fetchone()

    employees = conn.execute("""SELECT * 
                                FROM employees
                                WHERE empl_role = 'Cashier'
                                ORDER BY empl_surname""").fetchall()

    customer_cards = conn.execute("""SELECT *
                                     FROM customer_cards
                                     ORDER BY cust_surname""").fetchall()

    if request.method == "POST":
        id_employee = request.form["id_employee"]
        card_number = request.form.get("card_number")
        print_date = request.form["print_date"]
        sum_total = request.form["sum_total"]
        vat = request.form["vat"]
        try:
            conn.execute("""UPDATE receipts
                        SET id_employee = ?,
                            card_number = ?,
                            print_date = ?,
                            sum_total = ?,
                            vat = ?
                        WHERE check_number = ?""",
                     (id_employee, card_number if card_number else None, print_date, sum_total, vat, check_number))

            conn.commit()
            return jsonify({
                "success": True
            })

        except Exception as e:

            conn.rollback()

            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

        finally:
            conn.close()


@receipt_routes.route("/receipt/delete/<string:check_number>")
def delete_receipt(check_number):
    conn = get_db_connection()

    conn.execute("""DELETE FROM receipts
                    WHERE check_number = ?""", (check_number,))

    conn.commit()
    conn.close()
    return redirect(url_for("receipt_routes.receipts"))

@receipt_routes.route("/receipts/get/<string:check_number>")
def get_receipt(check_number):

    conn = get_db_connection()

    receipt = conn.execute("""
        SELECT *
        FROM receipts
        WHERE check_number = ?
    """, (check_number,)).fetchone()

    conn.close()

    return jsonify(dict(receipt))

@receipt_routes.route("/receipts/<check_number>/sales")
def get_receipt_sales(check_number):

    conn = get_db_connection()

    sales = conn.execute("""
         SELECT
            s.UPC,
            p.product_name,
            s.product_number,
            s.selling_price

        FROM sales s

        JOIN store_products sp
            ON sp.UPC = s.UPC

        JOIN products p
            ON p.id_product = sp.id_product

        WHERE s.check_number = ?
    """, (check_number,)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in sales])
@receipt_routes.route("/products/get-price/<upc>")
def get_price(upc):

    conn = get_db_connection()

    product = conn.execute("""
        SELECT selling_price
        FROM store_products
        WHERE UPC = ?
    """, (upc,)).fetchone()

    conn.close()

    return jsonify(dict(product))
