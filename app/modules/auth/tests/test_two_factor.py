import pytest
from flask import url_for

from app import db
from app.modules.auth.models import User
from app.modules.auth.services import AuthenticationService


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        pass
    yield test_client


def test_generate_totp_secret(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        secret = user.generate_totp_secret()

        assert secret is not None
        assert len(secret) == 32
        assert user.two_factor_secret == secret


def test_verify_totp_not_enabled(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        user.two_factor_enabled = False
        db.session.commit()

        result = user.verify_totp("123456")
        assert result is False


def test_generate_backup_codes(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        codes = user.generate_backup_codes(10)

        assert len(codes) == 10
        assert user.backup_codes is not None

        for code in codes:
            assert len(code) == 8


def test_verify_backup_code_valid(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        codes = user.generate_backup_codes(5)
        db.session.commit()

        first_code = codes[0]
        result = user.verify_backup_code(first_code)

        assert result is True


def test_verify_backup_code_invalid(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        user.generate_backup_codes(5)
        db.session.commit()

        result = user.verify_backup_code("INVALID123")

        assert result is False


def test_verify_backup_code_reuse(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        codes = user.generate_backup_codes(5)
        db.session.commit()

        first_code = codes[0]
        user.verify_backup_code(first_code)

        result = user.verify_backup_code(first_code)
        assert result is False


def test_setup_two_factor_service(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = AuthenticationService()

        qr_code, secret = service.setup_two_factor(user)

        assert qr_code is not None
        assert secret is not None
        assert user.two_factor_secret == secret


def test_disable_two_factor_service(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        user.two_factor_enabled = True
        user.two_factor_secret = "TESTSECRET123"
        db.session.commit()

        service = AuthenticationService()
        result = service.disable_two_factor(user)

        assert result is True
        assert user.two_factor_enabled is False
        assert user.two_factor_secret is None
        assert user.backup_codes is None


def test_two_factor_setup_step1_access(test_client):
    test_client.post("/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True)

    response = test_client.get("/profile/two-factor/setup/step1")
    assert response.status_code == 200
    assert b"Scan QR Code" in response.data

    test_client.get("/logout", follow_redirects=True)


def test_two_factor_setup_step2_requires_step1(test_client):
    test_client.post("/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True)

    with test_client.session_transaction() as sess:
        sess.pop('two_factor_setup_step', None)

    response = test_client.get("/profile/two-factor/setup/step2", follow_redirects=True)
    assert response.request.path == url_for("auth.setup_two_factor_step1")

    test_client.get("/logout", follow_redirects=True)


def test_two_factor_login_redirect(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        user.two_factor_enabled = True
        user.generate_totp_secret()
        db.session.commit()

    response = test_client.post(
        "/login",
        data=dict(email="test@example.com", password="test1234"),
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/login/two-factor" in response.location

    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        user.two_factor_enabled = False
        user.two_factor_secret = None
        db.session.commit()
