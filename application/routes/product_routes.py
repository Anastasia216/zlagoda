from flask import Blueprint, Flask, render_template, request, redirect, url_for, jsonify
from sqlite_db import get_db_connection
from application.decorators import login_required, role_required
product_routes = Blueprint("product_routes", __name__)

@product_routes.route("/products")
@login_required
@role_required("manager","cashier")
def products():
    search = request.args.get("search", "").strip()
    category_number = request.args.get("category_number", "").strip()

    conn = get_db_connection()
    categories = conn.execute("""
           SELECT *
           FROM categories
           ORDER BY category_name
       """).fetchall()

    if search and category_number:
        products = conn.execute("""
            SELECT p.id_product,
                   p.product_name,
                   c.category_name,
                   p.manufacturer,
                   p.characteristics
            FROM products p
            JOIN categories c
                 ON p.category_number = c.category_number
            WHERE (p.product_name LIKE ?
                OR p.manufacturer LIKE ?
                OR c.category_name LIKE ?
                ) AND p.category_number LIKE ?   
            ORDER BY p.product_name
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            category_number
        )).fetchall()

    elif search:
        products = conn.execute("""
                                SELECT p.id_product,
                                       p.product_name,
                                       c.category_name,
                                       p.manufacturer,
                                       p.characteristics
                                FROM products p
                                         JOIN categories c
                                              ON p.category_number = c.category_number
                                WHERE  p.product_name LIKE ?
                                        OR p.manufacturer LIKE ?
                                        OR c.category_name LIKE ?
                                ORDER BY p.product_name
                                """,
                                (f"%{search}%",
                                f"%{search}%",
                                f"%{search}%"
                                )).fetchall()

    elif category_number:
        products = conn.execute(""" 
                                SELECT p.id_product,
                                       p.product_name,
                                       c.category_name,
                                       p.manufacturer,
                                       p.characteristics
                                FROM products p
                                         JOIN categories c
                                              ON p.category_number = c.category_number
                                WHERE p.category_number = ?
                                ORDER BY p.product_name
        """,(category_number,)).fetchall()

    else:
        products = conn.execute("""
                    SELECT p.id_product,
                           p.product_name,
                           c.category_name,
                           p.manufacturer,
                           p.characteristics
                    FROM products p
                    JOIN categories c
                         ON p.category_number = c.category_number
                    ORDER BY p.product_name
                """).fetchall()
    conn.close()
    return render_template("products/products.html", products=products, categories=categories, search=search, category_number=category_number)


@product_routes.route("/products/add", methods=["POST"])
@login_required
@role_required("manager")
def add_product():
    conn = get_db_connection()
    category_number = request.form.get("category_number")
    manufacturer = request.form.get("manufacturer", "").strip()
    product_name = request.form.get("product_name", "").strip()
    characteristics = request.form.get("characteristics", "").strip()

    if not product_name or not manufacturer or not characteristics:
        conn.close()
        return jsonify({"success": False, "message": "All fields are required and cannot be empty!"}), 400

    if len(product_name) > 50 or len(manufacturer) > 50:  # Відповідно до структури БД (Varchar 50)
        conn.close()
        return jsonify({"success": False, "message": "Product name or Manufacturer is too long (max 50 chars)!"}), 400

    if len(characteristics) > 100:  # Відповідно до структури БД (Varchar 100)
        conn.close()
        return jsonify({"success": False, "message": "Characteristics are too long (max 100 chars)!"}), 400

    try:
        conn.execute("""INSERT INTO products (category_number, manufacturer, product_name, characteristics)
                        VALUES (?, ?, ?, ?)""", (category_number, manufacturer, product_name, characteristics))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@product_routes.route("/products/get/<int:id_product>")
@login_required
@role_required("manager","cashier")
def get_product(id_product):

    conn = get_db_connection()
    product = conn.execute("""
        SELECT *
        FROM products
        WHERE id_product = ?
    """, (id_product,)).fetchone()

    conn.close()
    return jsonify(dict(product))


@product_routes.route("/products/edit/<int:id_product>", methods=["POST"])
@login_required
@role_required("manager")
def edit_product(id_product):
    conn = get_db_connection()

    category_number = request.form.get("category_number")
    manufacturer = request.form.get("manufacturer", "").strip()
    product_name = request.form.get("product_name", "").strip()
    characteristics = request.form.get("characteristics", "").strip()

    if not product_name or not manufacturer or not characteristics:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Fields cannot be empty!"
        }), 400

    if (
        len(product_name) > 50
        or len(manufacturer) > 50
        or len(characteristics) > 100
    ):
        conn.close()
        return jsonify({
            "success": False,
            "message": "Input length exceeds database limits!"
        }), 400

    try:
        conn.execute(
            """
            UPDATE products
            SET category_number = ?,
                manufacturer = ?,
                product_name = ?,
                characteristics = ?
            WHERE id_product = ?
            """,
            (
                category_number,
                manufacturer,
                product_name,
                characteristics,
                id_product,
            ),
        )

        conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        conn.close()


@product_routes.route("/products/delete/<int:id_product>", methods=["POST"])
@login_required
@role_required("manager")
def delete_product(id_product):
    conn = get_db_connection()
    try:
        linked_store_items = conn.execute(
            "SELECT 1 FROM store_products WHERE id_product = ? LIMIT 1",
            (id_product,)
        ).fetchone()

        if linked_store_items:
            return jsonify({
                "success": False,
                "message": "Cannot delete this product because it is currently placed on the shop floor or warehouse (Store Products exist)."
            }), 400

        conn.execute("DELETE FROM products WHERE id_product = ?", (id_product,))
        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()