from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from sqlite_db import get_db_connection
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")
@app.route('/categories')
def categories():
    conn = get_db_connection()
    categories = conn.execute("""SELECT * FROM categories ORDER BY category_name""").fetchall()
    conn.close()
    return render_template("categories/categories.html", categories=categories)
    #return str([dict(row) for row in categories])
@app.route("/categories/add", methods=["GET", "POST"])
def add_category():
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["category_name"]
        conn.execute(""" INSERT INTO categories (category_name)VALUES (?)""", (name,))
        conn.commit()
        conn.close()
        return redirect(url_for("categories"))

    conn.close()
    return render_template("categories/add.html")

@app.route("/categories/edit/<int:id>", methods=["GET", "POST"])
def edit_category(id):
    conn = get_db_connection()
    category = conn.execute(""" SELECT * FROM categories WHERE category_number = ?""", (id,)).fetchone()
    if request.method == "POST":
        name = request.form["category_name"]
        conn.execute("""UPDATE categories SET category_name = ? WHERE category_number = ?""", (name, id))
        conn.commit()
        conn.close()

        return redirect(url_for("categories"))
    conn.close()
    return render_template("categories/edit.html", category=category)

@app.route("/categories/delete/<int:id>")
def delete_category(id):
    conn = get_db_connection()
    conn.execute("""DELETE FROM categories WHERE category_number = ?""", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("categories"))

if __name__ == "__main__":
    app.run(debug=True)