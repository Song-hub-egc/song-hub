from app import db
from app.modules.dataset.models import DataSet, PublicationType, Author
from sqlalchemy import Enum as SQLAlchemyEnum

class ImageDataset(DataSet):
    id = db.Column(db.Integer, db.ForeignKey('data_set.id'), primary_key=True)
    images = db.relationship("Image", backref="image_dataset", lazy=True, cascade="all, delete")

    __mapper_args__ = {
        'polymorphic_identity': 'image_dataset',
    }

    def files(self):
        return [file for img in self.images for file in img.files]

    def get_files_count(self):
        return sum(len(img.files) for img in self.images)

    def get_file_total_size(self):
        return sum(file.size for img in self.images for file in img.files)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_set_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)
    image_meta_data_id = db.Column(db.Integer, db.ForeignKey("image_meta_data.id"))
    
    # We will reuse Hubfile but we need to update Hubfile model to support this relationship
    # For now, we assume Hubfile will be updated to have image_id
    files = db.relationship("Hubfile", backref="image", lazy=True, cascade="all, delete")
    
    image_meta_data = db.relationship("ImageMetaData", uselist=False, backref="image", cascade="all, delete")

    def __repr__(self):
        return f"Image<{self.id}>"


class ImageMetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publication_type = db.Column(SQLAlchemyEnum(PublicationType), nullable=False)
    publication_doi = db.Column(db.String(120))
    tags = db.Column(db.String(120))
    
    authors = db.relationship(
        "Author", backref="image_metadata", lazy=True, cascade="all, delete", foreign_keys=[Author.image_meta_data_id]
    )

    def __repr__(self):
        return f"ImageMetaData<{self.title}>"
