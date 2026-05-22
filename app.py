from flask import Flask, render_template, request, redirect, url_for
from extensions import db, migrate
from sqlite_db import get_db_connection
def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("home.html")
    app.config.from_object("configure.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from database import models  # важливо: після init_app


    return app

#categories

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)