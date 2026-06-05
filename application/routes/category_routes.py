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

@category_routes.route("/categories/delete/<int:category_number>")
@login_required
@role_required("manager")
def delete_category(category_number):
    conn = get_db_connection()
    conn.execute("""DELETE FROM categories 
                    WHERE category_number = ?""", (category_number,))
    conn.commit()
    conn.close()

    return redirect(url_for("category_routes.categories"))
