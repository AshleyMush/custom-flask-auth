from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    session,
    request,
)
from flask_login import login_user, current_user, logout_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from .forms.auth import RegisterForm, LoginForm
from .models.user import User, db
from .utils.encryption import hash_and_salt_password, check_password_hash
from .utils.email_utils import send_password_reset_email


auth_bp = Blueprint(
    "auth_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    hide_registration = User.query.count() > 0

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return f"Already logged in. Welcome back, {current_user.first_name} ({current_user.email})"

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user and check_password_hash(user.password, password):
            flash("Logged in successfully", "success")
            login_user(user, remember=form.remember_me.data)
            return f"Login successful! Welcome, {user.first_name} ({user.role})"
        flash("Invalid email or password", "danger")

    return render_template("/auth/login.html", form=form, hide_registration=hide_registration)


@auth_bp.route("/logout")
def logout():
    """Log out the current user."""
    session.clear()
    logout_user()
    flash("You have been logged out successfully.", "success")
    return "You have been logged out successfully."


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    user_count = User.query.count()
    if user_count == 0:
        role = "Admin"
    else:
        flash("Registration is closed. ", "info")
        return "Registration is closed."

    if form.validate_on_submit() and form.data:
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            flash("Email already exists, Login instead", "danger")
            return "Email already exists. Please login instead."
        hashed_password = hash_and_salt_password(form.password.data)
        new_user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=hashed_password,
            role=role,
        )
        db.session.add(new_user)
        flash("Registered successfully", "success")
        db.session.commit()
        login_user(new_user)
        if new_user.role == "Admin":
            return f"Admin account registered: {new_user.first_name} ({new_user.email})"
        return f"User already registered: {new_user.first_name} ({new_user.email}). This is the Dashboard page."
    else:
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", "danger")
    return render_template("/auth/register.html", form=form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user.email)
            return redirect(url_for("auth_bp.login"))
        return redirect(url_for("auth_bp.forgot_password"))
    flash("If the email is registered, a password reset link has been sent", "info")
    return render_template("/auth/forgot-password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=3600)
    except SignatureExpired:
        flash("The password reset link has expired.", "danger")
        return redirect(url_for("auth_bp.forgot_password"))
    except BadSignature:
        flash("Invalid password reset link.", "danger")
        return redirect(url_for("auth_bp.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth_bp.reset_password", token=token))
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("auth_bp.reset_password", token=token))
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = hash_and_salt_password(password)
            db.session.commit()
            flash("Your password has been updated!", "success")
            return redirect(url_for("auth_bp.login"))
        flash("User not found.", "danger")
        return redirect(url_for("auth_bp.register"))
    return render_template("/auth/reset-password.html", token=token)