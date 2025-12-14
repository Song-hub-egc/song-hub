from flask import Blueprint

# Import models to ensure SQLAlchemy registers tables during app init/migrations
from app.modules.audiodataset import models  # noqa: F401

# Placeholder blueprint (not exposing routes yet)
audiodataset_bp = Blueprint("audiodataset", __name__)
