import secrets
from flask import Flask, render_template
from application.decorators import login_required

from application.routes.receipt_routes import receipt_routes
from extensions import db, migrate
import database.models
from application.routes.employee_routes import employee_routes
from application.routes.category_routes import category_routes
from application.routes.customer_card_routes import customer_card_routes
from application.routes.product_routes import product_routes
from application.routes.auth import auth
def create_app():
    app = Flask(__name__)

    app.register_blueprint(auth)
    app.register_blueprint(product_routes)
    app.register_blueprint(employee_routes)
    app.register_blueprint(category_routes)
    app.register_blueprint(customer_card_routes)
    app.register_blueprint(receipt_routes)
    @app.route("/")
    @login_required
    def home():
        return render_template("home.html")

    app.config.from_object("configure.Config")
    app.config["SESSION_PERMANENT"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        pass


    return app

#categories

app = create_app()

app.secret_key = secrets.token_urlsafe(32)

if __name__ == "__main__":
    app.run(debug=True)