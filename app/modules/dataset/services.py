import hashlib
import logging
import os
import shutil
import uuid
from typing import Optional

from flask import request

from app.modules.auth.services import AuthenticationService
from app.modules.dataset.models import DataSet, DSMetaData, DSViewRecord
from app.modules.dataset.repositories import (
    AuthorRepository,
    DataSetRepository,
    DOIMappingRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
)
from app.modules.featuremodel.repositories import FeatureModelRepository, FMMetaDataRepository
from app.modules.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)
from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)


def calculate_checksum_and_size(file_path):
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file:
        content = file.read()
        hash_md5 = hashlib.md5(content).hexdigest()
        return hash_md5, file_size


class DataSetService(BaseService):
    def __init__(self):
        super().__init__(DataSetRepository())
        self.feature_model_repository = FeatureModelRepository()
        self.author_repository = AuthorRepository()
        self.dsmetadata_repository = DSMetaDataRepository()
        self.fmmetadata_repository = FMMetaDataRepository()
        self.dsdownloadrecord_repository = DSDownloadRecordRepository()
        self.hubfiledownloadrecord_repository = HubfileDownloadRecordRepository()
        self.hubfilerepository = HubfileRepository()
        self.dsviewrecord_repostory = DSViewRecordRepository()
        self.hubfileviewrecord_repository = HubfileViewRecordRepository()

    def move_feature_models(self, dataset: DataSet):
        current_user = AuthenticationService().get_authenticated_user()
        source_dir = current_user.temp_folder()

        working_dir = os.getenv("WORKING_DIR", "")
        dest_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{dataset.id}")

        os.makedirs(dest_dir, exist_ok=True)

        if hasattr(dataset, "feature_models"):
            for feature_model in dataset.feature_models:
                uvl_filename = feature_model.fm_meta_data.uvl_filename
                shutil.move(os.path.join(source_dir, uvl_filename), dest_dir)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_synchronized(current_user_id)

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_unsynchronized(current_user_id)

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return self.repository.get_unsynchronized_dataset(current_user_id, dataset_id)

    def latest_synchronized(self):
        return self.repository.latest_synchronized()

    def count_synchronized_datasets(self):
        return self.repository.count_synchronized_datasets()

    def count_feature_models(self):
        return self.feature_model_service.count_feature_models()

    def count_authors(self) -> int:
        return self.author_repository.count()

    def count_dsmetadata(self) -> int:
        return self.dsmetadata_repository.count()

    def total_dataset_downloads(self) -> int:
        return self.dsdownloadrecord_repository.total_dataset_downloads()

    def total_dataset_views(self) -> int:
        return self.dsviewrecord_repostory.total_dataset_views()

    def get_trending_datasets(self, period="week", limit=10):
        period_days = 7 if period == "week" else 30 if period == "month" else 7

        trending_data = self.repository.get_trending_datasets(
            period_days=period_days,
            limit=limit,
        )

        result = []
        for dataset, downloads, views, total_activity in trending_data:
            authors = dataset.ds_meta_data.authors
            main_author = authors[0].name if authors else "Unknown"

            community = None
            if dataset.ds_meta_data.tags:
                tags = dataset.ds_meta_data.tags.split(",")
                community = tags[0].strip() if tags else None

            result.append(
                {
                    "id": dataset.id,
                    "title": dataset.ds_meta_data.title,
                    "main_author": main_author,
                    "community": community,
                    "downloads": int(downloads),
                    "views": int(views),
                    "total_activity": int(total_activity),
                    "dataset": dataset,
                }
            )

        return result

    def create_from_form(self, form, current_user) -> DataSet:
        main_author = {
            "name": f"{current_user.profile.surname}, {current_user.profile.name}",
            "affiliation": current_user.profile.affiliation,
            "orcid": current_user.profile.orcid,
        }
        try:
            logger.info(f"Creating dsmetadata...: {form.get_dsmetadata()}")
            dsmetadata = self.dsmetadata_repository.create(**form.get_dsmetadata())
            for author_data in [main_author] + form.get_authors():
                author = self.author_repository.create(commit=False, ds_meta_data_id=dsmetadata.id, **author_data)
                dsmetadata.authors.append(author)

            dataset_class = DataSet
            if hasattr(form, "feature_models"):
                from app.modules.featuremodel.models import UVLDataset
                dataset_class = UVLDataset
            elif hasattr(form, "images"):
                from app.modules.imagedataset.models import ImageDataset
                dataset_class = ImageDataset

            dataset = dataset_class(user_id=current_user.id, ds_meta_data_id=dsmetadata.id)
            self.repository.session.add(dataset)

            if hasattr(form, "feature_models"):
                for feature_model in form.feature_models:
                    uvl_filename = feature_model.uvl_filename.data
                    fmmetadata = self.fmmetadata_repository.create(commit=False, **feature_model.get_fmmetadata())
                    for author_data in feature_model.get_authors():
                        author = self.author_repository.create(
                            commit=False, fm_meta_data_id=fmmetadata.id, **author_data
                        )
                        fmmetadata.authors.append(author)

                    fm = self.feature_model_repository.create(
                        commit=False, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
                    )

                    # associated files in feature model
                    file_path = os.path.join(current_user.temp_folder(), uvl_filename)
                    checksum, size = calculate_checksum_and_size(file_path)

                    file = self.hubfilerepository.create(
                        commit=False, name=uvl_filename, checksum=checksum, size=size, feature_model_id=fm.id
                    )
                    fm.files.append(file)
            
            elif hasattr(form, "images"):
                from app.modules.imagedataset.models import Image, ImageMetaData
                from app.modules.dataset.models import PublicationType

                for image_form in form.images:
                    filename = image_form.filename.data
                    # Create generic metadata for image (reusing what we can or creating new)
                    image_metadata = ImageMetaData(
                        filename=filename,
                        title=image_form.title.data,
                        description=image_form.desc.data,
                        publication_type=PublicationType.NONE,  # Defaulting for now
                        tags="",
                        publication_doi=""
                    )

                    # Add main author to image metadata as well for now
                    author = self.author_repository.create(commit=False, image_meta_data_id=None, **main_author)
                    image_metadata.authors.append(author)

                    self.repository.session.add(image_metadata)
                    self.repository.session.flush()  # to get ID

                    # Fix author FK
                    author.image_meta_data_id = image_metadata.id

                    image = Image(data_set_id=dataset.id, image_meta_data_id=image_metadata.id)
                    self.repository.session.add(image)
                    self.repository.session.flush()

                    # associated files
                    file_path = os.path.join(current_user.temp_folder(), filename)
                    if os.path.exists(file_path):
                        checksum, size = calculate_checksum_and_size(file_path)

                        # Hubfile creation - note we need to pass image_id
                        # HubfileRepository might need update to accept image_id or we create manually
                        file = self.hubfilerepository.create(
                            commit=False,
                            name=filename,
                            checksum=checksum,
                            size=size,
                            image_id=image.id,
                            feature_model_id=None
                        )
                        image.files.append(file)
                    else:
                        logger.warning(f"File {filename} not found in temp folder")

            self.repository.session.commit()

        except Exception as exc:
            logger.info(f"Exception creating dataset from form...: {exc}")
            self.repository.session.rollback()
            raise exc
        return dataset

    def move_images(self, dataset: DataSet):
        current_user = AuthenticationService().get_authenticated_user()
        source_dir = current_user.temp_folder()

        working_dir = os.getenv("WORKING_DIR", "")
        dest_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{dataset.id}")

        os.makedirs(dest_dir, exist_ok=True)

        if hasattr(dataset, "images"):
            for image in dataset.images:
                filename = image.image_meta_data.filename
                source_path = os.path.join(source_dir, filename)
                if os.path.exists(source_path):
                    shutil.move(source_path, dest_dir)

    def update_dsmetadata(self, id, **kwargs):
        return self.dsmetadata_repository.update(id, **kwargs)

    def get_uvlhub_doi(self, dataset: DataSet) -> str:
        domain = os.getenv("DOMAIN", "localhost")
        return f"http://{domain}/doi/{dataset.ds_meta_data.dataset_doi}"

    def increment_download_count(self, dataset_id: int):
        """Increment the download count for a dataset"""
        return self.repository.increment_download_count(dataset_id)


class AuthorService(BaseService):
    def __init__(self):
        super().__init__(AuthorRepository())


class DSDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(DSDownloadRecordRepository())


class DSMetaDataService(BaseService):
    def __init__(self):
        super().__init__(DSMetaDataRepository())

    def update(self, id, **kwargs):
        return self.repository.update(id, **kwargs)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.repository.filter_by_doi(doi)


class DSViewRecordService(BaseService):
    def __init__(self):
        super().__init__(DSViewRecordRepository())

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.repository.the_record_exists(dataset, user_cookie)

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.repository.create_new_record(dataset, user_cookie)

    def create_cookie(self, dataset: DataSet) -> str:

        user_cookie = request.cookies.get("view_cookie")
        if not user_cookie:
            user_cookie = str(uuid.uuid4())

        existing_record = self.the_record_exists(dataset=dataset, user_cookie=user_cookie)

        if not existing_record:
            self.create_new_record(dataset=dataset, user_cookie=user_cookie)

        return user_cookie


class DOIMappingService(BaseService):
    def __init__(self):
        super().__init__(DOIMappingRepository())

    def get_new_doi(self, old_doi: str) -> str:
        doi_mapping = self.repository.get_new_doi(old_doi)
        if doi_mapping:
            return doi_mapping.dataset_doi_new
        else:
            return None


class SizeService:

    def __init__(self):
        pass

    def get_human_readable_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024**2:
            return f"{round(size / 1024, 2)} KB"
        elif size < 1024**3:
            return f"{round(size / (1024 ** 2), 2)} MB"
        else:
            return f"{round(size / (1024 ** 3), 2)} GB"
