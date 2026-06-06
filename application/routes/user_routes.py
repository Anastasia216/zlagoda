from uuid import uuid4

from flask import jsonify, Blueprint, render_template, request, redirect, url_for
from sqlite_db import get_db_connection
from werkzeug.security import generate_password_hash
user_routes = Blueprint("user_routes", __name__)
@user_routes.route("/users/add", methods=["POST"])
def add_user():

    id_employee = request.form["id_employee"]

    username = request.form["username"]

    password = request.form["password"]

    conn = get_db_connection()

    employee = conn.execute(
        """
        SELECT empl_role
        FROM employees
        WHERE id_employee = ?
        """,
        (id_employee,)
    ).fetchone()

    if employee is None:

        return jsonify(
            success=False,
            error="Employee not found"
        )


    id_user = str(uuid4())

    role = employee["empl_role"]

    password_hashed = generate_password_hash(
        password
    )

    conn.execute(
        """
        INSERT INTO users
        (
            id_user,
            id_employee,
            username,
            password_hash,
            role
        )
        VALUES
        (
            ?, ?, ?, ?, ?
        )
        """,
        (
            id_user,
            id_employee,
            username,
            password_hashed,
            role
        )
    )

    conn.commit()

    return jsonify(success=True)
