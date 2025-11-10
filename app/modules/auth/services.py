import os

from flask_login import current_user, login_user
import hashlib
from datetime import datetime, timedelta, timezone

from app import db
from app.modules.auth.models import User, UserSession
from app.modules.auth.repositories import UserRepository
from app.modules.profile.models import UserProfile
from app.modules.profile.repositories import UserProfileRepository
from core.configuration.configuration import uploads_folder_name
from core.services.BaseService import BaseService


class AuthenticationService(BaseService):
    def __init__(self):
        super().__init__(UserRepository())
        self.user_profile_repository = UserProfileRepository()

    def login(self, email, password, remember=True):
        user = self.repository.get_by_email(email)
        if user is not None and user.check_password(password):
            login_user(user, remember=remember)
            return True
        return False

    def is_email_available(self, email: str) -> bool:
        return self.repository.get_by_email(email) is None

    def create_with_profile(self, **kwargs):
        try:
            email = kwargs.pop("email", None)
            password = kwargs.pop("password", None)
            name = kwargs.pop("name", None)
            surname = kwargs.pop("surname", None)

            if not email:
                raise ValueError("Email is required.")
            if not password:
                raise ValueError("Password is required.")
            if not name:
                raise ValueError("Name is required.")
            if not surname:
                raise ValueError("Surname is required.")

            user_data = {"email": email, "password": password}

            profile_data = {
                "name": name,
                "surname": surname,
            }

            user = self.create(commit=False, **user_data)
            profile_data["user_id"] = user.id
            self.user_profile_repository.create(**profile_data)
            self.repository.session.commit()
        except Exception as exc:
            self.repository.session.rollback()
            raise exc
        return user

    def update_profile(self, user_profile_id, form):
        if form.validate():
            updated_instance = self.update(user_profile_id, **form.data)
            return updated_instance, None

        return None, form.errors

    def get_authenticated_user(self) -> User | None:
        if current_user.is_authenticated:
            return current_user
        return None

    def get_authenticated_user_profile(self) -> UserProfile | None:
        if current_user.is_authenticated:
            return current_user.profile
        return None

    def temp_folder_by_user(self, user: User) -> str:
        return os.path.join(uploads_folder_name(), "temp", str(user.id))

    def setup_two_factor(self, user: User) -> tuple[str, list[str]]:
        secret = user.generate_totp_secret()
        qr_code = user.get_qr_code()
        self.repository.session.commit()
        return qr_code, secret

    def enable_two_factor(self, user: User, token: str) -> bool:
        if not user.two_factor_secret:
            return False

        if not user.verify_totp(token, check_enabled=False):
            return False

        user.two_factor_enabled = True
        backup_codes = user.generate_backup_codes()
        self.repository.session.commit()
        return backup_codes

    def disable_two_factor(self, user: User) -> bool:
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.backup_codes = None
        self.repository.session.commit()
        return True

    def verify_two_factor_token(self, user: User, token: str, is_backup: bool = False) -> bool:
        if is_backup:
            return user.verify_backup_code(token)
        return user.verify_totp(token)

    def regenerate_backup_codes(self, user: User) -> list[str]:
        if not user.two_factor_enabled:
            return []
        backup_codes = user.generate_backup_codes()
        self.repository.session.commit()
        return backup_codes

class SessionService:

    def get_session_hash(self, session_id):
        return hashlib.sha256(session_id.encode()).hexdigest()

    def get_active_sessions(self, user):
        return UserSession.query.filter_by(user_id=user.id).filter(
            UserSession.expires_at > datetime.now(timezone.utc)
        ).order_by(UserSession.last_activity.desc()).all()

    def get_session_by_id(self, session_id, user):
        session_hash = self.get_session_hash(session_id)
        return UserSession.query.filter_by(
            session_id=session_hash,
            user_id=user.id
        ).first()

    def create_session(self, user, request, session_id):
        session_hash = self.get_session_hash(session_id)

        existing = UserSession.query.filter_by(session_id=session_hash).first()
        if existing:
            existing.update_activity()
            db.session.commit()
            return existing

        user_session = UserSession(
            user_id=user.id,
            session_id=session_hash,
            ip_address=self.get_client_ip(request),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        user_agent_string = request.headers.get('User-Agent', '')
        user_session.parse_user_agent(user_agent_string)

        location = self.get_location_from_ip(user_session.ip_address)
        user_session.location = location

        db.session.add(user_session)
        db.session.commit()

        return user_session

    def revoke_session(self, session_id, user):
        session_hash = self.get_session_hash(session_id)
        user_session = UserSession.query.filter_by(
            session_id=session_hash,
            user_id=user.id
        ).first()

        if user_session:
            db.session.delete(user_session)
            db.session.commit()
            return True
        return False

    def revoke_session_by_hash(self, session_hash, user):
        user_session = UserSession.query.filter_by(
            session_id=session_hash,
            user_id=user.id
        ).first()

        if user_session:
            from sqlalchemy import text

            db.session.delete(user_session)

            prefix = 'uvlhub:session:'
            session_key_pattern = f"{prefix}%"

            try:
                result = db.session.execute(
                    text("SELECT session_id, data FROM flask_sessions WHERE session_id LIKE :pattern"),
                    {"pattern": session_key_pattern}
                )

                for row in result:
                    flask_session_id = row[0]
                    session_data = row[1]

                    if session_data:
                        import pickle
                        try:
                            data = pickle.loads(session_data)
                            stored_id = data.get('_id', '')
                            stored_hash = hashlib.sha256(stored_id.encode()).hexdigest()

                            if stored_hash == session_hash:
                                db.session.execute(
                                    text("DELETE FROM flask_sessions WHERE session_id = :session_id"),
                                    {"session_id": flask_session_id}
                                )
                                break
                        except Exception:
                            continue
            except Exception:
                pass

            db.session.commit()
            return True
        return False

    def revoke_all_except_current(self, user, current_session_id):
        current_hash = self.get_session_hash(current_session_id)

        UserSession.query.filter(
            UserSession.user_id == user.id,
            UserSession.session_id != current_hash
        ).delete()

        db.session.commit()
        return True

    def update_session_activity(self, session_id, user):
        session_hash = self.get_session_hash(session_id)
        user_session = UserSession.query.filter_by(
            session_id=session_hash,
            user_id=user.id
        ).first()

        if user_session:
            user_session.update_activity()
            db.session.commit()

    def cleanup_expired_sessions(self):
        UserSession.query.filter(
            UserSession.expires_at < datetime.now(timezone.utc)
        ).delete()
        db.session.commit()

    def get_client_ip(self, request):
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        return request.remote_addr

    def get_location_from_ip(self, ip_address):
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            return "Local"

        try:
            import geoip2.database
            db_path = os.path.join(os.getcwd(), 'GeoLite2-City.mmdb')

            if not os.path.exists(db_path):
                return "Unknown"

            with geoip2.database.Reader(db_path) as reader:
                response = reader.city(ip_address)
                city = response.city.name or "Unknown"
                country = response.country.name or "Unknown"
                return f"{city}, {country}"
        except Exception:
            return "Unknown"

    def mark_as_current(self, session_id, user):
        session_hash = self.get_session_hash(session_id)

        UserSession.query.filter_by(user_id=user.id).update({'is_current': False})

        current_session = UserSession.query.filter_by(
            session_id=session_hash,
            user_id=user.id
        ).first()

        if current_session:
            current_session.is_current = True
            db.session.commit()

    def get_active_session_count(self, user):
        return UserSession.query.filter_by(user_id=user.id).filter(
            UserSession.expires_at > datetime.now(timezone.utc)
        ).count()
