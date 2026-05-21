from flask import Flask
from extensions import db, migrate
from sqlite_db import get_db_connection
def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        conn = get_db_connection()

        categories = conn.execute(
            "SELECT * FROM categories"
        ).fetchall()

        conn.close()

        result = ""

        for row in categories:
            result += f"{row['category_number']} - {row['category_name']}<br>"
        return result
    app.config.from_object("configure.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from database import models  # важливо: після init_app


    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)