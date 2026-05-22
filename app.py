from flask import Flask, render_template
from extensions import db, migrate
from application.routes.employee_routes import employee_routes
def create_app():
    app = Flask(__name__)

    app.register_blueprint(employee_routes)
    @app.route("/")
    def home():
        return render_template("home.html")

    app.config.from_object("configure.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        pass


    return app

#categories

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)