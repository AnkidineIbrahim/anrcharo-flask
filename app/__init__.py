from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name=None):
    import os
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Login config
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Connectez-vous pour accéder à cette page.'
    login_manager.login_message_category = 'warning'

    # Blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # User loader
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Jinja2 globals
    @app.context_processor
    def inject_globals():
        from app.models.models import Setting
        try:
            settings = {s.key: s.value for s in Setting.query.all()}
        except Exception:
            settings = {}
        return dict(site_settings=settings)

    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
