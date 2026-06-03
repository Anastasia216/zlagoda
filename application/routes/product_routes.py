from flask import Blueprint, Flask, render_template, request, redirect, url_for, jsonify
from sqlite_db import get_db_connection

product_routes = Blueprint("product_routes", __name__)

@product_routes.route("/products")
def products():
    search = request.args.get("search", "").strip()
    conn = get_db_connection()
    categories = conn.execute("""
           SELECT *
           FROM categories
           ORDER BY category_name
       """).fetchall()
    if search:
        products = conn.execute("""
            SELECT p.id_product,
                   p.product_name,
                   c.category_name,
                   p.manufacturer,
                   p.characteristics
            FROM products p
            JOIN categories c
                 ON p.category_number = c.category_number
            WHERE p.product_name LIKE ?
               OR p.manufacturer LIKE ?
               OR c.category_name LIKE ?
            ORDER BY p.product_name
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()
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
    return render_template("products/products.html", products=products, categories=categories, search=search)


@product_routes.route("/products/add", methods=["GET", "POST"])
def add_product():
    conn = get_db_connection()
    categories = conn.execute("""SELECT *
                                 FROM categories
                                 ORDER BY category_name """).fetchall()

    if request.method == "POST":
        category_number = request.form["category_number"]
        manufacturer = request.form["manufacturer"].strip()
        product_name = request.form["product_name"].strip()
        characteristics = request.form["characteristics"].strip()
        #validation
        if not product_name:
            conn.close()
            return "Product name cannot be empty"

        if len(product_name) > 100:
            conn.close()
            return "Product name is too long (max 100)"

        if not manufacturer:
            conn.close()
            return "Manufacturer cannot be empty"

        if len(manufacturer) > 100:
            conn.close()
            return "Manufacturer is too long (max 100)"

        if len(characteristics) > 500:
            conn.close()
            return "Characteristics are too long (max 500)"
        
        conn.execute("""INSERT INTO products ( 
                            category_number, 
                            manufacturer, 
                            product_name, 
                            characteristics)
                        VALUES (?, ?, ?, ?)""",
                     (category_number, manufacturer, product_name, characteristics))
        conn.commit()
        conn.close()

        return redirect(url_for("product_routes.products"))
    conn.close()
    return render_template("products/add.html", categories=categories)

@product_routes.route("/products/get/<int:id_product>")
def get_product(id_product):

    conn = get_db_connection()

    product = conn.execute("""
        SELECT *
        FROM products
        WHERE id_product = ?
    """, (id_product,)).fetchone()

    conn.close()

    return jsonify(dict(product))
@product_routes.route("/products/edit/<int:id_product>", methods=["GET", "POST"])
def edit_product(id_product):
    conn = get_db_connection()
    product = conn.execute("""SELECT *
                              FROM products
                              WHERE id_product = ?""", (id_product,)).fetchone()

    categories = conn.execute("""SELECT *
                                 FROM categories
                                 ORDER BY category_name""").fetchall()
    if request.method == "POST":
        category_number = request.form["category_number"]
        manufacturer = request.form["manufacturer"]
        product_name = request.form["product_name"]
        characteristics = request.form["characteristics"]

        conn.execute(""" UPDATE products
                         SET category_number = ?,
                             manufacturer    = ?,
                             product_name    = ?,
                             characteristics = ?
                         WHERE id_product = ?""", (category_number, manufacturer, product_name, characteristics, id_product))

        conn.commit()
        conn.close()
        return jsonify({
            "success": True
        })
    conn.close()
    return render_template("products/edit.html", product=product, categories=categories)


@product_routes.route("/products/delete/<int:id_product>")
def delete_product(id_product):
    conn = get_db_connection()
    conn.execute("""DELETE
                    FROM products
                    WHERE id_product = ?""", (id_product,))

    conn.commit()
    conn.close()
    return redirect(url_for("product_routes.products"))
