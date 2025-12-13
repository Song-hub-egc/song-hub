from sqlalchemy import Enum as SQLAlchemyEnum

from app import db
from app.modules.dataset.models import DataSet, PublicationType


class AudioDataset(DataSet):
    id = db.Column(db.Integer, db.ForeignKey("data_set.id"), primary_key=True)
    audios = db.relationship("Audio", backref="audio_dataset", lazy=True, cascade="all, delete")

    __mapper_args__ = {
        "polymorphic_identity": "audio_dataset",
    }

    def files(self):
        return [file for audio in self.audios for file in audio.files]

    def get_files_count(self):
        return sum(len(audio.files) for audio in self.audios)

    def get_file_total_size(self):
        return sum(file.size for audio in self.audios for file in audio.files)


class Audio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_set_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)
    audio_meta_data_id = db.Column(db.Integer, db.ForeignKey("audio_meta_data.id"))
    files = db.relationship("Hubfile", backref="audio", lazy=True, cascade="all, delete")
    audio_meta_data = db.relationship("AudioMetaData", uselist=False, backref="audio", cascade="all, delete")

    def __repr__(self):
        return f"Audio<{self.id}>"


class AudioMetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publication_type = db.Column(SQLAlchemyEnum(PublicationType), nullable=False)
    publication_doi = db.Column(db.String(120))
    tags = db.Column(db.String(120))

    authors = db.relationship(
        "Author", backref="audio_metadata", lazy=True, cascade="all, delete", foreign_keys="Author.audio_meta_data_id"
    )

    def __repr__(self):
        return f"AudioMetaData<{self.title}>"
