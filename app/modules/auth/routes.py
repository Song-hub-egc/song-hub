from flask import current_app, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.modules.auth import auth_bp
from app.modules.auth.forms import LoginForm, SignupForm, TwoFactorSetupForm, TwoFactorVerifyForm
from app.modules.auth.repositories import UserRepository
from app.modules.auth.services import AuthenticationService
from app.modules.auth.services import AuthenticationService, SessionService
from app.modules.profile.services import UserProfileService


authentication_service = AuthenticationService()
user_profile_service = UserProfileService()
session_service = SessionService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f"Email {email} in use")

        try:
            user = authentication_service.create_with_profile(**form.data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f"Error creating user: {exc}")

        # Log user
        login_user(user, remember=True)
        if not current_app.config.get("TESTING"):
            session_service.register_current_session(user)
        return redirect(url_for("public.index"))

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user_repository = UserRepository()
        user = user_repository.get_by_email(form.email.data)

        if user and user.check_password(form.password.data):
            if user.two_factor_enabled:
                session['pending_2fa_user_id'] = user.id
                session['remember_me'] = form.remember_me.data
                return redirect(url_for("auth.verify_two_factor"))
            else:
                login_user(user, remember=form.remember_me.data)
                if not current_app.config.get("TESTING"):
                    session_service.register_current_session(user)
                return redirect(url_for("public.index"))

        return render_template("auth/login_form.html", form=form, error="Invalid credentials")

    return render_template("auth/login_form.html", form=form)


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        session_id = session.get('_id')
        if session_id:
            try:
                session_service.revoke_session(session_id, current_user)
            except Exception:
                pass
    logout_user()
    session.pop('_last_activity_update', None)
    session.pop('_id', None)
    return redirect(url_for("public.index"))


@auth_bp.route("/login/two-factor", methods=["GET", "POST"])
def verify_two_factor():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    user_id = session.get('pending_2fa_user_id')
    if not user_id:
        return redirect(url_for("auth.login"))

    user_repository = UserRepository()
    user = user_repository.get_by_id(user_id)

    if not user or not user.two_factor_enabled:
        session.pop('pending_2fa_user_id', None)
        return redirect(url_for("auth.login"))

    form = TwoFactorVerifyForm()
    if request.method == "POST" and form.validate_on_submit():
        is_backup = form.use_backup_code.data
        if authentication_service.verify_two_factor_token(user, form.token.data, is_backup):
            remember = session.get('remember_me', False)
            session.pop('pending_2fa_user_id', None)
            session.pop('remember_me', None)
            login_user(user, remember=remember)
            if not current_app.config.get("TESTING"):
                session_service.register_current_session(user)
            return redirect(url_for("public.index"))

        return render_template("auth/two_factor_verify.html", form=form, error="Invalid authentication code")

    return render_template("auth/two_factor_verify.html", form=form)


@auth_bp.route("/profile/two-factor/setup", methods=["GET"])
@login_required
def setup_two_factor():
    if current_user.two_factor_enabled:
        return redirect(url_for("profile.my_profile"))

    qr_code, secret = authentication_service.setup_two_factor(current_user)
    session['two_factor_secret'] = secret

    return render_template("profile/two_factor_setup.html", qr_code=qr_code, secret=secret)


@auth_bp.route("/profile/two-factor/verify", methods=["POST"])
@login_required
def verify_two_factor_setup():
    if current_user.two_factor_enabled:
        return {"success": False, "error": "2FA already enabled"}, 400

    data = request.get_json()
    token = data.get('token', '')

    if not token:
        return {"success": False, "error": "Token is required"}, 400

    backup_codes = authentication_service.enable_two_factor(current_user, token)
    if backup_codes:
        session.pop('two_factor_secret', None)
        return {"success": True, "backup_codes": backup_codes}, 200

    return {"success": False, "error": "Invalid verification code"}, 400


@auth_bp.route("/profile/two-factor/disable", methods=["POST"])
@login_required
def disable_two_factor():
    authentication_service.disable_two_factor(current_user)
    return redirect(url_for("profile.my_profile"))


@auth_bp.route("/profile/two-factor/regenerate-backup-codes", methods=["POST"])
@login_required
def regenerate_backup_codes():
    if not current_user.two_factor_enabled:
        return redirect(url_for("profile.my_profile"))

    backup_codes = authentication_service.regenerate_backup_codes(current_user)
    return render_template("profile/two_factor_backup_codes.html", backup_codes=backup_codes)

@auth_bp.route("/sessions", methods=["GET"])
@login_required
def view_sessions():
    sessions = session_service.get_active_sessions(current_user)
    current_session_id = session.get('_id')
    current_session_hash = session_service.get_session_hash(current_session_id) if current_session_id else None

    return render_template("auth/sessions.html", sessions=sessions, current_session_hash=current_session_hash)


@auth_bp.route("/sessions/<session_identifier>/revoke", methods=["POST"])
@login_required
def revoke_session(session_identifier):
    current_session_id = session.get('_id')
    current_hash = session_service.get_session_hash(current_session_id) if current_session_id else None

    derived_identifier_hash = session_service.get_session_hash(session_identifier)
    if session_identifier == current_hash or derived_identifier_hash == current_hash:
        return jsonify({"success": False, "error": "Cannot revoke current session"}), 400

    success = session_service.revoke_session_by_hash(session_identifier, current_user)
    if not success:
        if derived_identifier_hash != session_identifier:
            success = session_service.revoke_session_by_hash(derived_identifier_hash, current_user)

    if success:
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "error": "Session not found"}), 404


@auth_bp.route("/sessions/revoke-all", methods=["POST"])
@login_required
def revoke_all_sessions():
    current_session_id = session.get('_id')

    if not current_session_id:
        return jsonify({"success": False, "error": "No active session"}), 400

    session_service.revoke_all_except_current(current_user, current_session_id)
    return jsonify({"success": True}), 200
