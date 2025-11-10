from datetime import datetime, timedelta, timezone

from flask import request, session
from flask_login import current_user

from app.modules.auth.services import SessionService


def setup_session_tracking(app):

    session_service = SessionService()

    @app.before_request
    def track_session():
        if request.path.startswith('/static'):
            return

        if current_user.is_authenticated:
            session_id = session.get('_id')

            if not session_id:
                return

            from flask_login import logout_user
            from flask import redirect, url_for
            from app.modules.auth.models import UserSession

            existing_session = session_service.get_session_by_id(session_id, current_user)

            if not existing_session:
                logout_user()
                session.clear()
                return redirect(url_for('auth.login'))
            else:
                last_update = session.get('_last_activity_update')
                now = datetime.now(timezone.utc)

                if not last_update or (now - datetime.fromisoformat(last_update)).total_seconds() > 30:
                    try:
                        session_service.update_session_activity(session_id, current_user)
                        session_service.mark_as_current(session_id, current_user)
                        session['_last_activity_update'] = now.isoformat()
                    except Exception:
                        pass