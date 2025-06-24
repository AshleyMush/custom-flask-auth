import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect
from models import db
from models.user import User
from controllers.dashboard import dashboard_bp
from controllers.auth import auth_bp
from controllers.portfolio import portfolio_bp
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate, upgrade

# Initialize Flask application
app = Flask(__name__)

# Define the base directory and ensure the instance folder exists
BASEDIR = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(BASEDIR, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Configure the database URI to point to the instance folder
app.config['SECRET_KEY'] = os.environ.get("SECRET_APP_KEY", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URI", f"sqlite:///{os.path.join(instance_path, 'Portfolio.db')}"
)


@app.before_first_request
def apply_migrations():
    with app.app_context():
        try:
            upgrade()  # Run migrations on startup
        except Exception as e:
            print(f"Migration error: {e}")


# Initialize extensions.
ckeditor = CKEditor(app)
Bootstrap5(app)
csrf = CSRFProtect(app)
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_bp.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# Register Blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(portfolio_bp)


# Initialize Flask-Migrate
# migrate = Migrate(app, db)

# Error Handler for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('dashboard/404.html'), 404

# Automatically create the database tables if they don't exist
with app.app_context():
    try:
        db.create_all()
    except SQLAlchemyError as e:
        db.session.rollback()


# Run the Application
if __name__ == "__main__":
    app.run(debug=True, port=5002)
