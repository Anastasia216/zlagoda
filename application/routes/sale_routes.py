from flask import Blueprint, Flask, render_template, request, redirect, url_for
from sqlite_db import get_db_connection

sale_routes = Blueprint("sale_routes",__name__)

@sale_routes.route("/sales")
def sales():
    conn = get_db_connection()
    sales = conn.execute("""SELECT s.UPC,
                                   s.check_number, 
                                   s.product_number,
                                   s.selling_price,
                                   
                                   p.product_name,
                                   r.print_date
                            FROM sales s
                                     JOIN store_products sp
                                          ON s.UPC = sp.UPC
                                     JOIN products p
                                          ON sp.id_product = p.id_product
                                     JOIN receipts r
                                          ON s.check_number = r.check_number
                            ORDER BY r.print_date DESC""").fetchall()
    conn.close()
    return render_template("sales/sales.html", sales=sales)


@sale_routes.route("/sales/add",methods=["GET", "POST"])
def add_sale():
    conn = get_db_connection()
    receipts = conn.execute("""SELECT *
                               FROM receipts
                               ORDER BY print_date DESC""").fetchall()

    products = conn.execute("""SELECT sp.UPC,
                                      p.product_name
                               FROM store_products sp
                                        JOIN products p
                                             ON sp.id_product = p.id_product
                               ORDER BY p.product_name""").fetchall()
    if request.method == "POST":
        upc = request.form["UPC"]
        check_number = request.form["check_number"]
        product_number = request.form["product_number"]
        selling_price = request.form["selling_price"]

        conn.execute("""INSERT INTO sales (UPC,
                                           check_number,
                                           product_number,
                                           selling_price)
                        VALUES (?, ?, ?, ?)""",
                     (upc, check_number, product_number, selling_price))

        conn.commit()
        conn.close()
        return redirect(url_for("sale_routes.sales"))

    conn.close()
    return render_template("sales/add.html", receipts=receipts, products=products)


@sale_routes.route("/sales/edit/<string:upc>/<string:check_number>",methods=["GET", "POST"])
def edit_sale(upc, check_number):
    conn = get_db_connection()
    sale = conn.execute("""SELECT *
                           FROM sales
                           WHERE UPC = ?
                             AND check_number = ?""",
                        (upc, check_number)).fetchone()

    receipts = conn.execute("""SELECT *
                               FROM receipts
                               ORDER BY print_date DESC""").fetchall()

    products = conn.execute("""SELECT sp.UPC,
                                      p.product_name
                               FROM store_products sp
                                        JOIN products p
                                             ON sp.id_product = p.id_product
                               ORDER BY p.product_name""").fetchall()

    if request.method == "POST":
        new_upc = request.form["UPC"]
        new_check_number = request.form["check_number"]
        product_number = request.form["product_number"]
        selling_price = request.form["selling_price"]

        conn.execute("""UPDATE sales
                        SET UPC = ?,
                            check_number = ?,
                            product_number = ?,
                            selling_price = ?
                        WHERE UPC = ?
                          AND check_number = ?""",
                     (new_upc, new_check_number, product_number, selling_price, upc, check_number))

        conn.commit()
        conn.close()
        return redirect(url_for("sale_routes.sales"))

    conn.close()
    return render_template("sales/edit.html", sale=sale, receipts=receipts, products=products)


@sale_routes.route("/sales/delete/<string:upc>/<string:check_number>")
def delete_sale(upc, check_number):
    conn = get_db_connection()
    conn.execute("""DELETE FROM sales
                    WHERE UPC = ?
                      AND check_number = ?""",
                 (upc, check_number))

    conn.commit()
    conn.close()
    return redirect(url_for("sale_routes.sales"))
