from datetime import datetime, timedelta, timezone

import pytest

from app import db
from app.modules.auth.models import User, UserSession
from app.modules.auth.services import SessionService


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        pass
    yield test_client


@pytest.fixture
def logged_in_client(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        if not user:
            user = User(email="test@example.com")
            user.set_password("test1234")
            db.session.add(user)
            db.session.commit()

    test_client.post("/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True)
    yield test_client
    test_client.get("/logout", follow_redirects=True)


def test_session_service_get_session_hash(test_client):
    with test_client.application.app_context():
        service = SessionService()
        session_id = "test_session_123"
        hash1 = service.get_session_hash(session_id)
        hash2 = service.get_session_hash(session_id)

        assert hash1 == hash2
        assert len(hash1) == 64


def test_session_service_create_session(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        from werkzeug.test import EnvironBuilder

        builder = EnvironBuilder(method="GET", path="/")
        env = builder.get_environ()

        with test_client.application.test_request_context(environ_base=env):
            from flask import request

            session_id = "test_session_create"
            user_session = service.create_session(user, request, session_id)

            assert user_session is not None
            assert user_session.user_id == user.id
            assert user_session.ip_address is not None


def test_session_service_get_active_sessions(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        UserSession.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        session_hash = service.get_session_hash("test_active_1")
        user_session = UserSession(
            user_id=user.id,
            session_id=session_hash,
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        db.session.add(user_session)
        db.session.commit()

        sessions = service.get_active_sessions(user)
        assert len(sessions) >= 1


def test_session_service_revoke_session(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        session_id = "test_revoke_session"
        session_hash = service.get_session_hash(session_id)

        user_session = UserSession(
            user_id=user.id,
            session_id=session_hash,
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        db.session.add(user_session)
        db.session.commit()

        result = service.revoke_session(session_id, user)
        assert result is True

        revoked_session = UserSession.query.filter_by(session_id=session_hash).first()
        assert revoked_session is None


def test_session_service_revoke_all_except_current(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        UserSession.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        current_session_id = "current_session"
        other_session_id_1 = "other_session_1"
        other_session_id_2 = "other_session_2"

        current_hash = service.get_session_hash(current_session_id)
        other_hash_1 = service.get_session_hash(other_session_id_1)
        other_hash_2 = service.get_session_hash(other_session_id_2)

        for session_hash in [current_hash, other_hash_1, other_hash_2]:
            user_session = UserSession(
                user_id=user.id,
                session_id=session_hash,
                ip_address="127.0.0.1",
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            )
            db.session.add(user_session)
        db.session.commit()

        service.revoke_all_except_current(user, current_session_id)

        remaining_sessions = UserSession.query.filter_by(user_id=user.id).all()
        assert len(remaining_sessions) == 1
        assert remaining_sessions[0].session_id == current_hash


def test_session_service_cleanup_expired_sessions(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        expired_hash = service.get_session_hash("expired_session")
        expired_session = UserSession(
            user_id=user.id,
            session_id=expired_hash,
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db.session.add(expired_session)
        db.session.commit()

        service.cleanup_expired_sessions()

        cleaned_session = UserSession.query.filter_by(session_id=expired_hash).first()
        assert cleaned_session is None


def test_view_sessions_authenticated(logged_in_client):
    response = logged_in_client.get("/sessions")
    assert response.status_code == 200
    assert b"Active Sessions" in response.data


def test_view_sessions_unauthenticated(test_client):
    response = test_client.get("/sessions", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.location


def test_revoke_session_authenticated(logged_in_client):
    with logged_in_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        session_id = "test_revoke_via_route"
        session_hash = service.get_session_hash(session_id)

        user_session = UserSession(
            user_id=user.id,
            session_id=session_hash,
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        db.session.add(user_session)
        db.session.commit()

    response = logged_in_client.post(f"/sessions/{session_id}/revoke")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_revoke_current_session_fails(logged_in_client):
    with logged_in_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        with logged_in_client.session_transaction() as sess:
            current_session_id = sess.get("_id")

        if current_session_id:
            session_hash = service.get_session_hash(current_session_id)

            user_session = UserSession(
                user_id=user.id,
                session_id=session_hash,
                ip_address="127.0.0.1",
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                is_current=True,
            )
            db.session.add(user_session)
            db.session.commit()

            response = logged_in_client.post(f"/sessions/{session_hash}/revoke")
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False


def test_revoke_all_sessions_authenticated(logged_in_client):
    with logged_in_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        UserSession.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        for i in range(3):
            session_hash = service.get_session_hash(f"test_session_{i}")
            user_session = UserSession(
                user_id=user.id,
                session_id=session_hash,
                ip_address="127.0.0.1",
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            )
            db.session.add(user_session)
        db.session.commit()

    response = logged_in_client.post("/sessions/revoke-all")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_user_session_model_update_activity(test_client):
    with test_client.application.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        service = SessionService()

        session_hash = service.get_session_hash("test_update_activity")
        user_session = UserSession(
            user_id=user.id,
            session_id=session_hash,
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        db.session.add(user_session)
        db.session.commit()

        old_activity = user_session.last_activity
        user_session.update_activity()

        assert user_session.last_activity > old_activity
