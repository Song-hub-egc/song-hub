import os
import uuid
from datetime import datetime, timezone

from flask import jsonify, make_response, request, send_from_directory
from flask_login import current_user

from app import db
from app.modules.hubfile import hubfile_bp
from app.modules.hubfile.models import HubfileDownloadRecord, HubfileViewRecord
from app.modules.hubfile.services import HubfileDownloadRecordService, HubfileService


@hubfile_bp.route("/file/download/<int:file_id>", methods=["GET"])
def download_file(file_id):
    hubfile_service = HubfileService()
    file = hubfile_service.get_or_404(file_id)
    file_path = hubfile_service.get_path_by_hubfile(file)

    if not file_path or not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    filename = os.path.basename(file_path)
    directory_path = os.path.dirname(file_path)

    # Get the cookie from the request or generate a new one if it does not exist
    user_cookie = request.cookies.get("file_download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())

    # Check if the download record already exists for this cookie
    existing_record = HubfileDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None, file_id=file_id, download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        HubfileDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            file_id=file_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    # Save the cookie to the user's browser
    resp = make_response(send_from_directory(directory=directory_path, path=filename, as_attachment=True))
    resp.set_cookie("file_download_cookie", user_cookie)

    return resp


@hubfile_bp.route("/file/view/<int:file_id>", methods=["GET"])
def view_file(file_id):
    hubfile_service = HubfileService()
    file = hubfile_service.get_or_404(file_id)
    absolute_path = hubfile_service.get_path_by_hubfile(file)

    try:
        if absolute_path and os.path.exists(absolute_path):
            _, ext = os.path.splitext(absolute_path)
            filename = os.path.basename(absolute_path)
            directory_path = os.path.dirname(absolute_path)

            # For non-text files (e.g., images) stream the file; for text/uvl return content as before.
            if ext.lower() not in {".uvl", ".txt"}:
                return send_from_directory(directory_path, filename)

            with open(absolute_path, "r") as f:
                content = f.read()

            user_cookie = request.cookies.get("view_cookie")
            if not user_cookie:
                user_cookie = str(uuid.uuid4())

            # Check if the view record already exists for this cookie
            existing_record = HubfileViewRecord.query.filter_by(
                user_id=current_user.id if current_user.is_authenticated else None,
                file_id=file_id,
                view_cookie=user_cookie,
            ).first()

            if not existing_record:
                # Register file view
                new_view_record = HubfileViewRecord(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    file_id=file_id,
                    view_date=datetime.now(),
                    view_cookie=user_cookie,
                )
                db.session.add(new_view_record)
                db.session.commit()

            # Prepare response
            response = jsonify({"success": True, "content": content})
            if not request.cookies.get("view_cookie"):
                response = make_response(response)
                response.set_cookie("view_cookie", user_cookie, max_age=60 * 60 * 24 * 365 * 2)

            return response
        else:
            return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
