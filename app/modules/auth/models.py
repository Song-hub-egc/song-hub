import base64
import io
import json
import secrets
from datetime import datetime

import pyotp
import qrcode
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow())

    two_factor_secret = db.Column(db.String(32), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    backup_codes = db.Column(db.Text, nullable=True)

    data_sets = db.relationship("DataSet", backref="user", lazy=True)
    profile = db.relationship("UserProfile", backref="user", uselist=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if "password" in kwargs:
            self.set_password(kwargs["password"])

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def temp_folder(self) -> str:
        from app.modules.auth.services import AuthenticationService

        return AuthenticationService().temp_folder_by_user(self)

    def generate_totp_secret(self) -> str:
        self.two_factor_secret = pyotp.random_base32()
        return self.two_factor_secret

    def get_totp_uri(self) -> str:
        if not self.two_factor_secret:
            return ""
        return pyotp.totp.TOTP(self.two_factor_secret).provisioning_uri(
            name=self.email,
            issuer_name="UVLHUB.IO"
        )

    def verify_totp(self, token: str, check_enabled: bool = True) -> bool:
        if not self.two_factor_secret:
            return False
        if check_enabled and not self.two_factor_enabled:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token, valid_window=1)

    def generate_backup_codes(self, count: int = 10) -> list[str]:
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        hashed_codes = [generate_password_hash(code) for code in codes]
        self.backup_codes = json.dumps(hashed_codes)
        return codes

    def verify_backup_code(self, code: str) -> bool:
        if not self.backup_codes:
            return False

        hashed_codes = json.loads(self.backup_codes)
        for idx, hashed_code in enumerate(hashed_codes):
            if check_password_hash(hashed_code, code.upper()):
                hashed_codes.pop(idx)
                self.backup_codes = json.dumps(hashed_codes)
                db.session.commit()
                return True
        return False

    def get_qr_code(self) -> str:
        uri = self.get_totp_uri()
        if not uri:
            return ""

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    device_type = db.Column(db.String(50), nullable=True)
    browser = db.Column(db.String(100), nullable=True)
    os = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow())
    last_activity = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow())
    is_current = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="sessions", lazy=True)

    def parse_user_agent(self, user_agent_string):
        from user_agents import parse
        user_agent = parse(user_agent_string)

        self.device_type = 'mobile' if user_agent.is_mobile else 'tablet' if user_agent.is_tablet else 'desktop'
        self.browser = user_agent.browser.family
        self.os = user_agent.os.family
        self.user_agent = user_agent_string

    def is_expired(self):
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def update_activity(self):
        self.last_activity = datetime.utcnow()

    def get_device_icon(self):
        if self.device_type == 'mobile':
            return 'fa-mobile'
        elif self.device_type == 'tablet':
            return 'fa-tablet'
        return 'fa-laptop'

    def get_time_since_activity(self):
        delta = datetime.utcnow() - self.last_activity
        if delta.total_seconds() < 60:
            return "Just now"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = int(delta.total_seconds() / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
