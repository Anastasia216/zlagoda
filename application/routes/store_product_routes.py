from flask import Blueprint, Flask, render_template, request, redirect, url_for, jsonify
from sqlite_db import get_db_connection
from application.decorators import login_required, role_required

store_product_routes = Blueprint('store_product_routes', __name__)


@store_product_routes.route("/store_products")
@login_required
@role_required("manager", "cashier")
def store_products():
    conn = get_db_connection()

    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "").strip()
    promo = request.args.get("promo", "").strip()

    products = conn.execute("""
                            SELECT id_product, product_name
                            FROM products
                            ORDER BY product_name
                            """).fetchall()

    all_existing_upcs = conn.execute("""
                                     SELECT sp.UPC, p.product_name, sp.promotional_product
                                     FROM store_products sp
                                              JOIN products p ON sp.id_product = p.id_product
                                     ORDER BY p.product_name
                                     """).fetchall()

    sql_base = """
               SELECT sp.UPC,
                      sp.UPC_prom,
                      sp.id_product,
                      sp.selling_price,
                      sp.products_number,
                      sp.promotional_product,
                      p.product_name,
                      p.manufacturer
               FROM store_products sp
                        JOIN products p ON sp.id_product = p.id_product \
               """

    where_clauses = []
    params = []

    if search:
        where_clauses.append("(sp.UPC LIKE ? OR p.product_name LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    if promo == "yes":
        where_clauses.append("sp.promotional_product = 1")
    elif promo == "no":
        where_clauses.append("sp.promotional_product = 0")

    sql = sql_base
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    if sort == "name":
        sql += " ORDER BY p.product_name ASC"
    elif sort == "quantity":
        sql += " ORDER BY sp.products_number DESC"
    else:
        sql += " ORDER BY sp.products_number DESC"  # Дефолт за кількістю [cite: 100]

    store_products = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template(
        "store_products/store_products.html",
        store_products=store_products,
        products=products,
        all_existing_upcs=all_existing_upcs,  # Передаємо в HTML
        search=search,
        sort=sort,
        promo=promo
    )


@store_product_routes.route("/store_products/add", methods=["POST"])
@login_required
@role_required("manager")
def add_store_product():
    conn = get_db_connection()
    upc = request.form["UPC"]
    products_number = request.form["products_number"]

    promotional_product = request.form.get("promotional_product")
    promotional_product = 1 if promotional_product else 0

    try:
        if promotional_product == 1:
            upc_prom_form = request.form.get("UPC_prom")
            if not upc_prom_form:
                return jsonify({"success": False, "message": "Обов'язково оберіть оригінальний товар з магазину!"})

            original_item = conn.execute(
                "SELECT id_product, selling_price FROM store_products WHERE UPC = ?", (upc_prom_form,)).fetchone()

            if not original_item:
                return jsonify({"success": False, "message": "Оригінальний товар не знайдено."})

            id_product = original_item["id_product"]
            selling_price = round(original_item["selling_price"] * 0.8, 2)

            upc_prom_value = None

        else:
            id_product = request.form["id_product"]
            selling_price = float(request.form["selling_price"])
            upc_prom_value = None  # Спочатку порожньо, поки не створили акційну пару

        conn.execute("""
                     INSERT INTO store_products(UPC, UPC_prom, id_product, selling_price, products_number,
                                                promotional_product)
                     VALUES (?, ?, ?, ?, ?, ?)
                     """, (upc, upc_prom_value, id_product, selling_price, products_number, promotional_product))

        if promotional_product == 1:
            conn.execute("""
                         UPDATE store_products
                         SET UPC_prom = ?
                         WHERE UPC = ?
                         """, (upc, upc_prom_form))

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()

@store_product_routes.route("/store_products/edit/<string:upc>", methods=["POST"])
@login_required
@role_required("manager")
def edit_store_product(upc):
    conn = get_db_connection()
    upc_prom = request.form.get("UPC_prom")
    id_product = request.form["id_product"]
    selling_price = float(request.form["selling_price"])
    products_number = request.form["products_number"]

    promotional_product = request.form.get("promotional_product")
    promotional_product = 1 if promotional_product else 0

    if promotional_product == 1:
        selling_price = round(selling_price * 0.8, 2)

    try:
        conn.execute("""
                     UPDATE store_products
                     SET UPC_prom            = ?,
                         id_product          = ?,
                         selling_price       = ?,
                         products_number     = ?,
                         promotional_product = ?
                     WHERE UPC = ?
                     """,
                     (
                         upc_prom if upc_prom and upc_prom != "" else None,
                         id_product,
                         selling_price,
                         products_number,
                         promotional_product,
                         upc
                     ))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()

@store_product_routes.route("/store_products/get/<string:upc>")
@login_required
@role_required("manager","cashier")
def get_store_product(upc):

    conn = get_db_connection()
    store_product = conn.execute("""SELECT *
                                    FROM store_products
                                    WHERE UPC = ?
                                 """, (upc,)).fetchone()

    conn.close()
    return jsonify(dict(store_product))

@store_product_routes.route("/store_products/delete/<string:upc>", methods=["POST"])
@login_required
@role_required("manager")
def delete_store_product(upc):
    conn = get_db_connection()
    conn.execute("""
        DELETE FROM store_products
        WHERE UPC = ?
    """, (upc,))
    conn.commit()
    conn.close()
    return jsonify({
        "success": True
    })


@store_product_routes.route("/store_products/analytics/quantity", methods=["GET"])
@login_required
@role_required("manager")
def get_product_sales_quantity():
    id_product = request.args.get("id")
    start_date = request.args.get("start")
    end_date = request.args.get("end")

    if not id_product or not start_date or not end_date:
        return jsonify({"success": False, "message": "All fields (product, start date, end date) are required."})

    conn = get_db_connection()
    try:
        sql = """
              SELECT COALESCE(SUM(s.product_number), 0) AS total_units_sold
              FROM sales s
                       JOIN receipts r ON s.check_number = r.check_number
                       JOIN store_products sp ON s.UPC = sp.UPC
              WHERE sp.id_product = ?
                AND r.print_date BETWEEN ? AND ?
              """

        start_param = f"{start_date} 00:00:00"
        end_param = f"{end_date} 23:59:59"

        result = conn.execute(sql, (id_product, start_param, end_param)).fetchone()
        total_sold = result["total_units_sold"] if result else 0

        return jsonify({"success": True, "total_sold": total_sold})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()