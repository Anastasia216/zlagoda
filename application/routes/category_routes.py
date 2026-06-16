from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlite_db import get_db_connection
from application.decorators import login_required, role_required

category_routes = Blueprint("category_routes", __name__)

@category_routes.route('/categories')
@login_required
@role_required("manager","cashier")
def categories():
    search = request.args.get("search", "").strip()
    conn = get_db_connection()
    if search:

        categories = conn.execute("""
                                SELECT *
                                FROM categories
                                WHERE category_name LIKE ?
                                ORDER BY category_name
                            """, (f"%{search}%",)).fetchall()

    else:

        categories = conn.execute("""SELECT * 
                                 FROM categories 
                                 ORDER BY category_name
                              """).fetchall()
    conn.close()
    return render_template("categories/categories.html", categories=categories, search=search)

@category_routes.route("/categories/add", methods=["GET", "POST"])
@login_required
@role_required("manager")
def add_category():
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["category_name"]
        conn.execute(""" INSERT INTO categories (category_name)
                        VALUES (?)""", (name,))
        conn.commit()
        category_id = conn.execute("""
                SELECT last_insert_rowid()
            """).fetchone()[0]
        conn.close()
        return jsonify({
            "success": True,
            "category_number": category_id
    })
    conn.close()
    return render_template("categories/add.html")

@category_routes.route("/categories/get/<int:category_number>")
@login_required
@role_required("manager","cashier")
def get_category(category_number):

    conn = get_db_connection()

    category = conn.execute("""
        SELECT *
        FROM categories
        WHERE category_number = ?
    """, (category_number,)).fetchone()

    conn.close()

    return jsonify(dict(category))

@category_routes.route("/categories/edit/<int:category_number>", methods=["GET", "POST"])
@login_required
@role_required("manager")
def edit_category(category_number):
    conn = get_db_connection()
    category = conn.execute(""" SELECT * 
                                FROM categories 
                                WHERE category_number = ?""", (category_number,)).fetchone()
    if request.method == "POST":
        name = request.form["category_name"]
        conn.execute("""UPDATE categories 
                        SET category_name = ? 
                        WHERE category_number = ?""", (name, category_number))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True
        })
    conn.close()
    return render_template("categories/add.html")


@category_routes.route("/categories/delete/<int:category_number>", methods=["POST"])
@login_required
@role_required("manager")
def delete_category(category_number):
    conn = get_db_connection()
    try:
        linked_products = conn.execute(
            "SELECT 1 FROM products WHERE category_number = ? LIMIT 1",
            (category_number,)
        ).fetchone()

        if linked_products:
            return jsonify({
                "success": False,
                "message": "Cannot delete this category because there are active products registered under it in the catalog."
            }), 400

        conn.execute("DELETE FROM categories WHERE category_number = ?", (category_number,))
        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


@category_routes.route('/categories/analytics/revenue', methods=['POST'])
@login_required
@role_required("manager", "cashier")
def category_revenue_analytics():
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()

    if not start_date or not end_date:
        return jsonify({"success": False, "message": "Please specify both start and end dates."}), 400

    conn = get_db_connection()
    try:
        rows = conn.execute("""
                            SELECT c.category_name,
                                   SUM(s.product_number)                   AS total_sold,
                                   SUM(s.product_number * s.selling_price) AS total_revenue
                            FROM categories c
                                     INNER JOIN products p ON c.category_number = p.category_number
                                     INNER JOIN store_products sp ON p.id_product = sp.id_product
                                     INNER JOIN sales s ON sp.UPC = s.UPC
                                     INNER JOIN receipts r ON s.check_number = r.check_number
                            WHERE r.print_date BETWEEN ? AND ?
                            GROUP BY c.category_name
                            ORDER BY total_revenue DESC 
                            """, (start_date, end_date)).fetchall()

        results_list = [
            {
                "category_name": row["category_name"],
                "total_sold": row["total_sold"],
                "total_revenue": float(row["total_revenue"])
            } for row in rows
        ]
        return jsonify({"success": True, "results": results_list})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


@category_routes.route('/categories/analytics/coverage', methods=['POST'])
@login_required
@role_required("manager")
def category_coverage_analytics():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
                            SELECT c.category_name
                            FROM categories c
                            WHERE NOT EXISTS (SELECT p.id_product
                                              FROM products p
                                              WHERE p.category_number = c.category_number
                                                AND NOT EXISTS (SELECT s.UPC
                                                                FROM store_products sp
                                                                         INNER JOIN sales s ON sp.UPC = s.UPC
                                                                WHERE sp.id_product = p.id_product))
                            """).fetchall()

        results_list = [{"category_name": row["category_name"]} for row in rows]
        return jsonify({"success": True, "results": results_list})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()