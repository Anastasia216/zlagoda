import uuid
from flask import session
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlite_db import get_db_connection
import json
from datetime import date, datetime, timedelta
from application.decorators import login_required, role_required

receipt_routes = Blueprint("receipt_routes", __name__)


@receipt_routes.route("/receipts")
@login_required
@role_required("manager", "cashier")
def receipts():
    conn = get_db_connection()

    search = request.args.get("search", "").strip()
    filter_type = request.args.get("filter_type", "")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    user_role = session.get("role")
    user_employee_id = session.get("employee_id")

    # Допоміжні дані для UI (Кастомні селекти)
    employees = conn.execute("""
                             SELECT *
                             FROM employees
                             WHERE LOWER(empl_role) = 'cashier'
                             ORDER BY empl_surname
                             """).fetchall()

    customer_cards = conn.execute("""
                                  SELECT *
                                  FROM customer_cards
                                  ORDER BY cust_surname
                                  """).fetchall()

    products = conn.execute("""
                            SELECT sp.UPC,
                                   sp.products_number,
                                   sp.promotional_product,
                                   p.product_name
                            FROM store_products sp
                                     JOIN products p ON p.id_product = sp.id_product
                            ORDER BY p.product_name
                            """).fetchall()

    query = """
            SELECT r.*,
                   e.empl_surname,
                   e.empl_name,
                   c.cust_surname,
                   c.cust_name
            FROM receipts r
                     JOIN employees e ON r.id_employee = e.id_employee
                     LEFT JOIN customer_cards c ON r.card_number = c.card_number
            """

    where_clauses = []
    params = []

    if user_role == "cashier":
        where_clauses.append("r.id_employee = ?")
        params.append(user_employee_id)

    if search:
        where_clauses.append("(r.check_number LIKE ? OR e.empl_surname LIKE ? OR c.cust_surname LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    if filter_type == "today":
        today_str = date.today().isoformat()
        where_clauses.append("date(r.print_date) = ?")
        params.append(today_str)
    elif filter_type == "period" and date_from and date_to:
        where_clauses.append("date(r.print_date) BETWEEN ? AND ?")
        params.extend([date_from, date_to])

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " ORDER BY r.print_date DESC"
    receipts_list = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "receipts/receipts.html",
        receipts=receipts_list,
        search=search,
        employees=employees,
        customer_cards=customer_cards,
        products=products
    )


@receipt_routes.route("/receipts/add", methods=["POST"])
@login_required
@role_required("manager", "cashier")
def add_receipt():
    conn = get_db_connection()
    if request.method == "POST":
        check_number = str(uuid.uuid4())[:10]

        employee_id = session.get("employee_id")
        if not employee_id:
            conn.close()
            return jsonify({"success": False, "message": "Unauthorized. Employee session expired."}), 401

        card_number = request.form.get("card_number")
        print_date = request.form["print_date"]

        products = json.loads(request.form["products"])
        if not products:
            conn.close()
            return jsonify({"success": False, "message": "Add at least one product."}), 400

        subtotal = 0
        for product in products:
            upc = product["upc"]
            quantity_to_buy = int(product["quantity"])
            price = float(product["price"])

            store_item = conn.execute("SELECT products_number FROM store_products WHERE UPC = ?", (upc,)).fetchone()
            if not store_item:
                conn.close()
                return jsonify({"success": False, "message": f"Product UPC {upc} not found."}), 400

            current_stock = store_item["products_number"]
            if current_stock < quantity_to_buy:
                conn.close()
                return jsonify(
                    {"success": False, "message": f"Not enough stock for UPC {upc}. Floor has: {current_stock}"}), 400

            subtotal += quantity_to_buy * price

        discount_percent = 0
        if card_number and card_number.strip() != "":
            card_data = conn.execute("SELECT percent FROM customer_cards WHERE card_number = ?",
                                     (card_number,)).fetchone()
            if card_data:
                discount_percent = int(card_data["percent"])

        sum_total = round(subtotal * (1 - (discount_percent / 100.0)), 2)

        vat = round(sum_total * 0.20, 2)

        try:
            conn.execute("""INSERT INTO receipts (check_number, id_employee, card_number, print_date, sum_total, vat)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                         (check_number, employee_id, card_number if card_number else None, print_date, sum_total, vat))

            for product in products:
                upc = product["upc"]
                quantity = int(product["quantity"])
                price = float(product["price"])

                conn.execute("""INSERT INTO sales(UPC, check_number, product_number, selling_price)
                                VALUES (?, ?, ?, ?)""", (upc, check_number, quantity, price))

                conn.execute("""UPDATE store_products
                                SET products_number = products_number - ?
                                WHERE UPC = ?""", (quantity, upc))

            conn.commit()
            return jsonify({"success": True})
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()


@receipt_routes.route("/receipts/<string:check_number>/sales")
@login_required
def get_receipt_sales(check_number):
    conn = get_db_connection()

    receipt_info = conn.execute("""
                                SELECT r.sum_total, r.vat, r.card_number, COALESCE(c.percent, 0) as percent
                                FROM receipts r
                                         LEFT JOIN customer_cards c ON r.card_number = c.card_number
                                WHERE r.check_number = ?
                                """, (check_number,)).fetchone()

    if not receipt_info:
        conn.close()
        return jsonify({"success": False, "message": "Receipt not found"}), 404

    sales_rows = conn.execute("""
                              SELECT s.product_number, s.selling_price, p.product_name, s.UPC
                              FROM sales s
                                       JOIN store_products sp ON s.UPC = sp.UPC
                                       JOIN products p ON sp.id_product = p.id_product
                              WHERE s.check_number = ?
                              """, (check_number,)).fetchall()

    subtotal = 0
    sales_list = []
    for row in sales_rows:
        subtotal += row["product_number"] * row["selling_price"]
        sales_list.append({
            "upc": row["UPC"],
            "product_name": row["product_name"],
            "product_number": row["product_number"],
            "selling_price": float(row["selling_price"])
        })

        discount_percent = int(receipt_info["percent"])
        sum_total = float(receipt_info["sum_total"])

        discount_currency = round(subtotal - sum_total, 2)
        if discount_currency < 0:
            discount_currency = 0.0

        correct_vat = round(sum_total * 0.20, 2)

        conn.close()

        return jsonify({
            "success": True,
            "sales": sales_list,
            "financials": {
                "subtotal": round(subtotal, 2),
                "discount_percent": discount_percent,
                "discount_currency": discount_currency,
                "sum_total": sum_total,
                "vat": correct_vat  # Тепер тут завжди буде правильне ПДВ після знижки!
            }
        })


@receipt_routes.route("/receipts/delete/<string:check_number>")
@login_required
@role_required("manager")
def delete_receipt(check_number):
    conn = get_db_connection()
    try:
        sales_items = conn.execute("SELECT UPC, product_number FROM sales WHERE check_number = ?",
                                   (check_number,)).fetchall()
        for item in sales_items:
            conn.execute("UPDATE store_products SET products_number = products_number + ? WHERE UPC = ?",
                         (item["product_number"], item["UPC"]))

        conn.execute("DELETE FROM receipts WHERE check_number = ?", (check_number,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"Database error during deletion: {str(e)}", 500
    finally:
        conn.close()

    return redirect(url_for("receipt_routes.receipts"))


@receipt_routes.route("/manager/receipts/analytics/data")
@login_required
@role_required("manager")
def get_analytics_data():
    cashier_id = request.args.get("cashier_id", "all")
    start = request.args.get("start", "")
    end = request.args.get("end", "")

    conn = get_db_connection()
    where_clauses = []
    params = []

    if cashier_id != "all":
        where_clauses.append("r.id_employee = ?")
        params.append(cashier_id)

    if start and end:
        where_clauses.append("date(r.print_date) BETWEEN ? AND ?")
        params.extend([start, end])

    where_str = ""
    if where_clauses:
        where_str = " WHERE " + " AND ".join(where_clauses)

    sql_calc = f"""
        SELECT COALESCE(SUM(r.sum_total), 0) AS revenue, COALESCE(SUM(r.vat), 0) AS vat_total
        FROM receipts r {where_str}
    """
    total_data = conn.execute(sql_calc, params).fetchone()
    revenue = float(total_data["revenue"]) if total_data else 0.0
    vat = float(total_data["vat_total"]) if total_data else 0.0

    sql_receipts = f"""
        SELECT r.check_number, r.print_date, r.sum_total, e.empl_surname || ' ' || e.empl_name AS cashier_name
        FROM receipts r JOIN employees e ON r.id_employee = e.id_employee {where_str} ORDER BY r.print_date DESC
    """
    receipts_rows = conn.execute(sql_receipts, params).fetchall()

    receipts_list = []
    for row in receipts_rows:
        receipts_list.append({
            "check_number": row["check_number"],
            "print_date": str(row["print_date"]),
            "sum_total": float(row["sum_total"]),
            "cashier_name": row["cashier_name"]
        })

    conn.close()
    return jsonify({"success": True, "revenue": revenue, "vat": vat, "receipts": receipts_list})


@receipt_routes.route("/api/manager/cashiers")
@login_required
@role_required("manager")
def get_cashiers_api():
    conn = get_db_connection()
    rows = conn.execute("""
                        SELECT id_employee, empl_surname, empl_name
                        FROM employees
                        WHERE LOWER(empl_role) = 'cashier'
                        ORDER BY empl_surname
                        """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
