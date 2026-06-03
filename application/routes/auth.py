from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import check_password_hash

from sqlite_db import get_db_connection

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute("""
            SELECT id_user,
                   username,
                   password_hash,
                   role
            FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        conn.close()

        if user and check_password_hash(user["password_hash"], password):

            session["user_id"] = user["id_user"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect("/")

        flash("Invalid username or password")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/login")