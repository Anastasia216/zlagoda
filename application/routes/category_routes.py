from flask import Blueprint, render_template, request, redirect, url_for
from sqlite_db import get_db_connection

category_routes = Blueprint("category_routes", __name__)

@category_routes.route('/categories')
def categories():
    conn = get_db_connection()
    categories = conn.execute("""SELECT * 
                                 FROM categories 
                                 ORDER BY category_name
                              """).fetchall()
    conn.close()
    return render_template("categories/categories.html", categories=categories)

@category_routes.route("/categories/add", methods=["GET", "POST"])
def add_category():
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["category_name"]
        conn.execute(""" INSERT INTO categories (category_name)
                        VALUES (?)""", (name,))
        conn.commit()
        conn.close()
        return redirect(url_for("category_routes.categories"))

    conn.close()
    return render_template("categories/add.html")

@category_routes.route("/categories/edit/<int:category_number>", methods=["GET", "POST"])
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

        return redirect(url_for("category_routes.categories"))
    conn.close()
    return render_template("categories/edit.html", category=category)

@category_routes.route("/categories/delete/<int:category_number>")
def delete_category(category_number):
    conn = get_db_connection()
    conn.execute("""DELETE FROM categories 
                    WHERE category_number = ?""", (category_number,))
    conn.commit()
    conn.close()

    return redirect(url_for("category_routes.categories"))
