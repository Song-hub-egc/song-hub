import os

from flask import current_app

from app.modules.auth.models import User
from app.modules.dataset.models import DataSet
from app.modules.hubfile.models import Hubfile
from app.modules.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)
from core.services.BaseService import BaseService


class HubfileService(BaseService):
    def __init__(self):
        super().__init__(HubfileRepository())
        self.hubfile_view_record_repository = HubfileViewRecordRepository()
        self.hubfile_download_record_repository = HubfileDownloadRecordRepository()

    def get_owner_user_by_hubfile(self, hubfile: Hubfile) -> User:
        return self.repository.get_owner_user_by_hubfile(hubfile)

    def get_dataset_by_hubfile(self, hubfile: Hubfile) -> DataSet:
        return self.repository.get_dataset_by_hubfile(hubfile)

    def get_path_by_hubfile(self, hubfile: Hubfile) -> str:

        hubfile_user = self.get_owner_user_by_hubfile(hubfile)
        hubfile_dataset = self.get_dataset_by_hubfile(hubfile)
        # Default to parent directory of app if WORKING_DIR is not set
        working_dir = os.getenv("WORKING_DIR") or os.path.dirname(current_app.root_path)

        path = os.path.join(
            working_dir, "uploads", f"user_{hubfile_user.id}", f"dataset_{hubfile_dataset.id}", hubfile.name
        )

        return os.path.abspath(path)

    def total_hubfile_views(self) -> int:
        return self.hubfile_view_record_repository.total_hubfile_views()

    def total_hubfile_downloads(self) -> int:
        hubfile_download_record_repository = HubfileDownloadRecordRepository()
        return hubfile_download_record_repository.total_hubfile_downloads()


class HubfileDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(HubfileDownloadRecordRepository())
