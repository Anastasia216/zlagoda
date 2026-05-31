from flask import Blueprint, Flask, render_template, request, redirect, url_for
from sqlite_db import get_db_connection

store_product_routes = Blueprint('store_product_routes', __name__)

@store_product_routes.route("/store_products")
def store_products():
    conn = get_db_connection()

    #Filters
    upc = request.args.get("UPC", "").strip()
    promotional = request.args.get("promotional", "").strip()
    sort = request.args.get("sort", "").strip()
    product_name = request.args.get("product_name", "").strip()

    query = """SELECT sp.UPC,
                      sp.UPC_prom,
                      sp.selling_price,
                      sp.products_number,
                      sp.promotional_product,
                      
                      p.product_name,
                      p.manufacturer
               FROM store_products sp
                JOIN products p
                     ON sp.id_product = p.id_product
               WHERE 1=1"""
    params =[]
    #search by upc
    if upc:
        query += """
        AND sp.UPC
        LIKE ?"""
        params.append(f"%{upc}%")

    #search by product_name
    if product_name:
        query += """
        AND p.product_name
        LIKE ?"""
        params.append(
            f"%{product_name}%"
        )

    #promotional
    if promotional == "yes":
        query += """
        AND sp.promotional_product = 1"""
    #non_promotional
    elif promotional == "no":
        query += """
        AND sp.promotional_product = 0"""

    #sort
    if sort == "name":
        query += """
        ORDER BY p.product_name"""
    else:
        query += """
        ORDER BY sp.products_number DESC"""


    store_products = conn.execute(query, params).fetchall()

    conn.close()
    return render_template("store_products/store_products.html",store_products=store_products)


@store_product_routes.route("/store_products/add", methods=["GET", "POST"])
def add_store_product():
    conn = get_db_connection()
    products = conn.execute("""SELECT *
                               FROM products 
                               ORDER BY product_name""").fetchall()

    all_upc = conn.execute(""" SELECT UPC
                               FROM store_products""").fetchall()

    if request.method == "POST":
        upc = request.form["UPC"]
        upc_prom = request.form["UPC_prom"]
        id_product = request.form["id_product"]
        selling_price = request.form["selling_price"]
        products_number = request.form["products_number"]
        promotional_product = request.form.get("promotional_product")
        promotional_product = (1 if promotional_product else 0)

        conn.execute("""INSERT INTO store_products (UPC,   
                                                    UPC_prom,
                                                    id_product,
                                                    selling_price,
                                                    products_number,
                                                    promotional_product)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (upc, upc_prom if upc_prom else None, id_product, selling_price, products_number, promotional_product))
        conn.commit()
        conn.close()
        return redirect(url_for("store_product_routes.store_products"))

    conn.close()
    return render_template("store_products/add.html",products=products, all_upc=all_upc)


@store_product_routes.route("/store_products/edit/<string:upc>", methods=["GET", "POST"])
def edit_store_product(upc):
    conn = get_db_connection()
    store_product = conn.execute("""SELECT *
                                    FROM store_products
                                    WHERE UPC = ?""", (upc,)).fetchone()

    products = conn.execute("""SELECT *
                               FROM products
                               ORDER BY product_name""").fetchall()

    all_upc = conn.execute("""SELECT UPC
                              FROM store_products""").fetchall()
    if request.method == "POST":
        upc_prom = request.form["UPC_prom"]
        id_product = request.form["id_product"]
        selling_price = request.form["selling_price"]
        products_number = request.form["products_number"]
        promotional_product = request.form.get("promotional_product")
        promotional_product = ( 1 if promotional_product else 0 )

        conn.execute("""UPDATE store_products
                        SET UPC_prom = ?,
                            id_product = ?,
                            selling_price = ?,
                            products_number = ?,
                            promotional_product = ?
                        WHERE UPC = ? """,
                      (upc_prom if upc_prom else None, id_product, selling_price, products_number, promotional_product, upc))

        conn.commit()
        conn.close()
        return redirect(url_for("store_product_routes.store_products"))

    conn.close()
    return render_template("store_products/edit.html", store_product=store_product, products=products, all_upc=all_upc)


@store_product_routes.route("/store_products/delete/<string:upc>")
def delete_store_product(upc):
    conn = get_db_connection()

    conn.execute("""DELETE FROM store_products
                    WHERE UPC = ?""", (upc,))

    conn.commit()
    conn.close()
    return redirect(url_for("store_product_routes.store_products"))