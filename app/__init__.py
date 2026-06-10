from flask import Flask, redirect, url_for

from .config import Config
from .extensions import db, login_manager
from .models import User, seed_data


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar o sistema."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes.auth import bp as auth_bp
    from .routes.dashboard import bp as dashboard_bp
    from .routes.clients import bp as clients_bp
    from .routes.vehicles import bp as vehicles_bp
    from .routes.services import bp as services_bp
    from .routes.users import bp as users_bp
    from .routes.appointments import bp as appointments_bp
    from .routes.work_orders import bp as work_orders_bp
    from .routes.inventory import bp as inventory_bp
    from .routes.sales import bp as sales_bp
    from .routes.api import bp as api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(work_orders_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.index"))

    @app.cli.command("init-db")
    def init_db_command():
        """Cria tabelas e carrega dados iniciais."""
        with app.app_context():
            db.create_all()
            seed_data()
            print("Banco inicializado com sucesso.")

    @app.context_processor
    def inject_globals():
        return {"app_name": app.config.get("APP_NAME", "Oficina AI")}

    return app
