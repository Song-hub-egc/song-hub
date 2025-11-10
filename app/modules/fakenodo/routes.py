from flask import jsonify, render_template, request
from werkzeug.utils import secure_filename

from app.modules.fakenodo import fakenodo_bp
from app.modules.fakenodo.services import fakenodo_service


@fakenodo_bp.route("/fakenodo", methods=["GET"])
def index():
    return render_template("fakenodo/index.html")


@fakenodo_bp.route("/fakenodo/test", methods=["GET"])
def zenodo_test() -> dict:
    """Return a small status JSON for the local fake Zenodo service."""
    return jsonify(fakenodo_service.status())


@fakenodo_bp.route("/fakenodo/api/deposit/depositions", methods=["POST"])
def create_deposition():
    """Create a deposition with the provided metadata."""
    payload = request.get_json(force=True, silent=True) or {}
    metadata = payload.get("metadata", {})
    created = fakenodo_service.create_deposition(metadata)
    return jsonify(created), 201


@fakenodo_bp.route("/fakenodo/api/deposit/depositions", methods=["GET"])
def list_depositions():
    return jsonify(fakenodo_service.list_depositions())


@fakenodo_bp.route("/fakenodo/api/deposit/depositions/<int:deposition_id>", methods=["GET"])
def get_deposition(deposition_id: int):
    deposition = fakenodo_service.get_deposition(deposition_id)
    if not deposition:
        return jsonify({"message": "Not found"}), 404
    return jsonify(deposition)


@fakenodo_bp.route("/fakenodo/api/deposit/depositions/<int:deposition_id>", methods=["PUT", "PATCH"])
def update_deposition(deposition_id: int):
    payload = request.get_json(force=True, silent=True) or {}
    metadata = payload.get("metadata")
    if metadata is None or not isinstance(metadata, dict):
        return jsonify({"message": "metadata payload required"}), 400

    updated = fakenodo_service.update_metadata(deposition_id, metadata)
    if not updated:
        return jsonify({"message": "Not found"}), 404
    return jsonify(updated)


@fakenodo_bp.route("/fakenodo/api/deposit/depositions/<int:deposition_id>", methods=["DELETE"])
def delete_deposition(deposition_id: int):
    deleted = fakenodo_service.delete_deposition(deposition_id)
    if not deleted:
        return jsonify({"message": "Not found"}), 404
    return "", 204


@fakenodo_bp.route("/fakenodo/api/deposit/depositions/<int:deposition_id>/files", methods=["POST"])
def upload_file(deposition_id: int):
    """Accept a file upload (stores only filename for diff detection)."""
    if "file" not in request.files:
        return jsonify({"message": "No file provided"}), 400

    current_file = request.files["file"]
    filename = secure_filename(current_file.filename or "unnamed")
    entry = fakenodo_service.add_file(deposition_id, filename)
    if not entry:
        return jsonify({"message": "Not found"}), 404
    return jsonify(entry), 201


@fakenodo_bp.route("/fakenodo/api/deposit/depositions/<int:deposition_id>/actions/publish", methods=["POST"])
def publish_deposition(deposition_id: int):
    """Mirror Zenodo publish semantics: new DOI only when files change."""
    result = fakenodo_service.publish(deposition_id)
    if not result:
        return jsonify({"message": "Not found"}), 404
    payload, is_new_version = result
    return jsonify(payload), 202 if is_new_version else 200


@fakenodo_bp.route("/fakenodo/api/deposit/depositions/<int:deposition_id>/versions", methods=["GET"])
def list_versions(deposition_id: int):
    versions = fakenodo_service.list_versions(deposition_id)
    if versions is None:
        return jsonify({"message": "Not found"}), 404
    return jsonify(versions)
