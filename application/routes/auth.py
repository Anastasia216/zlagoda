from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import check_password_hash

from sqlite_db import get_db_connection
from application.decorators import login_required

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute("""
            SELECT id_user, 
                   id_employee,
                   username,
                   password_hash,
                   role
            FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        conn.close()

        if user and check_password_hash(user["password_hash"], password):

            session["user_id"] = user["id_user"]
            session["employee_id"] = user["id_employee"]
            session["username"] = user["username"]
            session["role"] = user["role"].lower()


            session.permanent = False
            return redirect("/")

        flash("Invalid username or password")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@auth.route("/profile")
@login_required
def profile():

    conn = get_db_connection()

    employee = conn.execute("""
        SELECT *
        FROM employees
        WHERE id_employee = ?
    """, (session["employee_id"],)).fetchone()

    conn.close()

    return jsonify(dict(employee))
