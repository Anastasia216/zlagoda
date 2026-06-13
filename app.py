import os
import sys

if sys.platform == 'darwin':
    os.environ['PATH'] = '/opt/homebrew/bin:/usr/local/bin:' + os.environ.get('PATH', '')
    import cffi

    original_dlopen = cffi.FFI.dlopen

    def patched_dlopen(self, name, flags=0):
        if name and any(lib in name for lib in ['gobject', 'pango', 'cairo', 'glib', 'harfbuzz', 'fontconfig']):
            possible_dirs = ['/opt/homebrew/lib/', '/usr/local/lib/']
            for base_dir in possible_dirs:
                clean_name = name.replace('lib', '').split('.')[
                    0]
                variants = [
                    f"{base_dir}{name}",
                    f"{base_dir}lib{clean_name}.dylib",
                    f"{base_dir}lib{clean_name}.0.dylib"
                ]
                if 'gobject' in name:
                    variants.append(f"{base_dir}libgobject-2.0.0.dylib")
                    variants.append(f"{base_dir}libgobject-2.0.dylib")
                if 'pango' in name:
                    variants.append(f"{base_dir}libpango-1.0.0.dylib")
                    variants.append(f"{base_dir}libpango-1.0.dylib")
                if 'cairo' in name:
                    variants.append(f"{base_dir}libcairo.2.dylib")
                    variants.append(f"{base_dir}libcairo.dylib")

                for variant in variants:
                    try:
                        if os.path.exists(variant):
                            return original_dlopen(self, variant, flags)
                    except Exception:
                        continue
        return original_dlopen(self, name, flags)
    cffi.FFI.dlopen = patched_dlopen
import secrets
from flask import Flask, render_template
from application.decorators import login_required

from application.routes.receipt_routes import receipt_routes
from application.routes.store_product_routes import store_product_routes
from extensions import db, migrate
import database.models
from application.routes.employee_routes import employee_routes
from application.routes.category_routes import category_routes
from application.routes.customer_card_routes import customer_card_routes
from application.routes.product_routes import product_routes
from application.routes.user_routes import user_routes
from application.routes.auth import auth
from application.routes.report_routes import report_routes
def create_app():
    app = Flask(__name__)

    app.register_blueprint(user_routes)
    app.register_blueprint(auth)
    app.register_blueprint(product_routes)
    app.register_blueprint(employee_routes)
    app.register_blueprint(category_routes)
    app.register_blueprint(customer_card_routes)
    app.register_blueprint(receipt_routes)
    app.register_blueprint(store_product_routes)
    app.register_blueprint(report_routes)
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