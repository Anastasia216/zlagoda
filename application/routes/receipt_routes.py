from flask import Blueprint, Flask, render_template, request, redirect, url_for, jsonify
from sqlite_db import get_db_connection

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

    conn.close()
    return render_template("receipts/receipts.html", receipts=receipts, employees=employees, customer_cards=customer_cards, search=search)


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
        check_number = request.form["check_number"]
        id_employee = request.form["id_employee"]
        card_number = request.form.get("card_number")
        print_date = request.form["print_date"]
        sum_total = request.form["sum_total"]
        vat = request.form["vat"]

        conn.execute("""INSERT INTO receipts (check_number,
                                              id_employee,
                                              card_number,
                                              print_date,
                                              sum_total,
                                              vat)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (check_number, id_employee, card_number if card_number else None, print_date, sum_total, vat))

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

        conn.execute("""UPDATE receipts
                        SET id_employee = ?,
                            card_number = ?,
                            print_date = ?,
                            sum_total = ?,
                            vat = ?
                        WHERE check_number = ?""",
                     (id_employee, card_number if card_number else None, print_date, sum_total, vat, check_number))

        conn.commit()
        conn.close()
        return jsonify({
            "success": True
        })

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