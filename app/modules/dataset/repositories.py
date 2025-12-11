import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from flask_login import current_user
from sqlalchemy import desc, func

from app.modules.dataset.models import Author, DataSet, DOIMapping, DSDownloadRecord, DSMetaData, DSViewRecord
from core.repositories.BaseRepository import BaseRepository

logger = logging.getLogger(__name__)


class AuthorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Author)


class DSDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSDownloadRecord)

    def total_dataset_downloads(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0


class DSMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSMetaData)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.model.query.filter_by(dataset_doi=doi).first()


class DSViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSViewRecord)

    def total_dataset_views(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.model.query.filter_by(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_cookie=user_cookie,
        ).first()

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_date=datetime.now(timezone.utc),
            view_cookie=user_cookie,
        )


class DataSetRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.isnot(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.is_(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DataSet.id == dataset_id, DSMetaData.dataset_doi.is_(None))
            .first()
        )

    def count_synchronized_datasets(self):
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.isnot(None)).count()

    def count_unsynchronized_datasets(self):
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.is_(None)).count()

    def latest_synchronized(self):
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .order_by(desc(self.model.id))
            .limit(5)
            .all()
        )

    def get_trending_datasets(self, period_days: int = 7, limit: int = 10):
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=period_days)

        downloads_subquery = (
            self.session.query(
                DSDownloadRecord.dataset_id, func.count(func.distinct(DSDownloadRecord.id)).label("download_count")
            )
            .filter(DSDownloadRecord.download_date >= cutoff_date)
            .group_by(DSDownloadRecord.dataset_id)
            .subquery()
        )

        views_subquery = (
            self.session.query(DSViewRecord.dataset_id, func.count(func.distinct(DSViewRecord.id)).label("view_count"))
            .filter(DSViewRecord.view_date >= cutoff_date)
            .group_by(DSViewRecord.dataset_id)
            .subquery()
        )

        total_activity_col = func.coalesce(downloads_subquery.c.download_count, 0) + func.coalesce(
            views_subquery.c.view_count, 0
        )

        result = (
            self.session.query(
                DataSet,
                func.coalesce(downloads_subquery.c.download_count, 0).label("downloads"),
                func.coalesce(views_subquery.c.view_count, 0).label("views"),
                total_activity_col.label("total_activity"),
            )
            .join(DSMetaData, DataSet.ds_meta_data_id == DSMetaData.id)
            .outerjoin(downloads_subquery, DataSet.id == downloads_subquery.c.dataset_id)
            .outerjoin(views_subquery, DataSet.id == views_subquery.c.dataset_id)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .filter(total_activity_col > 0)
            .order_by(desc(total_activity_col))
            .limit(limit)
            .all()
        )

        return result

    def increment_download_count(self, dataset_id: int):
        """Increment the download count for a dataset"""
        dataset = self.model.query.filter_by(id=dataset_id).first()
        if dataset:
            dataset.download_count += 1
            self.session.commit()
        return dataset


class DOIMappingRepository(BaseRepository):
    def __init__(self):
        super().__init__(DOIMapping)

    def get_new_doi(self, old_doi: str) -> str:
        return self.model.query.filter_by(dataset_doi_old=old_doi).first()

class DatasetCommentRepository(BaseRepository):
    def __init__(self):
        from app.modules.dataset.models import DatasetComment
        super().__init__(DatasetComment)

    def get_dataset_comments(self, dataset_id: int, include_deleted: bool = False):
        """Get comments for a dataset"""
        query = self.model.query.filter_by(dataset_id=dataset_id)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.order_by(self.model.created_at.desc()).all()

    def get_user_comments(self, user_id: int):
        """Get all comments by a user"""
        return self.model.query.filter_by(user_id=user_id, is_deleted=False).order_by(self.model.created_at.desc()).all()

    def soft_delete_comment(self, comment_id: int, deleted_by: int):
        """Soft delete a comment"""
        from datetime import datetime
        comment = self.get_by_id(comment_id)
        if comment:
            comment.is_deleted = True
            comment.deleted_at = datetime.utcnow()
            comment.deleted_by = deleted_by
            self.session.commit()
        return comment

    def update_comment(self, comment_id: int, content: str):
        """Update comment content"""
        from datetime import datetime
        comment = self.get_by_id(comment_id)
        if comment and not comment.is_deleted:
            if comment.content != content:
                comment.content = content
                comment.updated_at = datetime.utcnow()
                self.session.commit()
        return comment
