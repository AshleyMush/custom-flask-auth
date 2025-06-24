import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap5
from flask_migrate import upgrade
from sqlalchemy.exc import SQLAlchemyError

from models import db
from models.user import User
from custom_flask_auth.auth import auth_bp  # Only auth for now

# Initialize Flask application
app = Flask(__name__)

# Define instance folder
BASEDIR = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(BASEDIR, 'instance')
os.makedirs(instance_path, exist_ok=True)

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get("SECRET_APP_KEY", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URI", f"sqlite:///{os.path.join(instance_path, 'User_Auth.db')}"
)

# Auto-run migrations on startup
@app.before_first_request
def apply_migrations():
    with app.app_context():
        try:
            upgrade()
        except Exception as e:
            print(f"Migration error: {e}")

# Initialize extensions
ckeditor = CKEditor(app)
Bootstrap5(app)
csrf = CSRFProtect(app)
db.init_app(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_bp.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# Register blueprints
app.register_blueprint(auth_bp)

# TODO: Register `dashboard_bp/ admin_dashboard` when dashboard module is ready
# from custom_flask_auth.dashboard import dashboard_bp
# app.register_blueprint(dashboard_bp)

# TODO: Register `portfolio_bp/ user_dashboard` when portfolio module is ready
# from custom_flask_auth.portfolio import portfolio_bp
# app.register_blueprint(portfolio_bp)

# Optional: Custom error handlers
@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404  # Simplified for now
    #return render_template('404.html'), 404


# Auto-create tables
with app.app_context():
    try:
        db.create_all()
    except SQLAlchemyError as e:
        db.session.rollback()

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5002)
