from sqlalchemy import Enum as SQLAlchemyEnum

from app import db

from app.modules.dataset.models import Author, PublicationType, DataSet


class UVLDataset(DataSet):
    id = db.Column(db.Integer, db.ForeignKey('data_set.id'), primary_key=True)
    feature_models = db.relationship("FeatureModel", backref="uvl_dataset", lazy=True, cascade="all, delete")

    __mapper_args__ = {
        'polymorphic_identity': 'uvl_dataset',
    }

    def files(self):
        return [file for fm in self.feature_models for file in fm.files]

    def get_files_count(self):
        return sum(len(fm.files) for fm in self.feature_models)

    def get_file_total_size(self):
        return sum(file.size for fm in self.feature_models for file in fm.files)


class FeatureModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_set_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)
    fm_meta_data_id = db.Column(db.Integer, db.ForeignKey("fm_meta_data.id"))
    files = db.relationship("Hubfile", backref="feature_model", lazy=True, cascade="all, delete")
    fm_meta_data = db.relationship("FMMetaData", uselist=False, backref="feature_model", cascade="all, delete")

    def __repr__(self):
        return f"FeatureModel<{self.id}>"


class FMMetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uvl_filename = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publication_type = db.Column(SQLAlchemyEnum(PublicationType), nullable=False)
    publication_doi = db.Column(db.String(120))
    tags = db.Column(db.String(120))
    uvl_version = db.Column(db.String(120))
    fm_metrics_id = db.Column(db.Integer, db.ForeignKey("fm_metrics.id"))
    fm_metrics = db.relationship("FMMetrics", uselist=False, backref="fm_meta_data")
    authors = db.relationship(
        "Author", backref="fm_metadata", lazy=True, cascade="all, delete", foreign_keys=[Author.fm_meta_data_id]
    )

    def __repr__(self):
        return f"FMMetaData<{self.title}"


class FMMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solver = db.Column(db.Text)
    not_solver = db.Column(db.Text)

    def __repr__(self):
        return f"FMMetrics<solver={self.solver}, not_solver={self.not_solver}>"
