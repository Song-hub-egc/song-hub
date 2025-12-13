import hashlib
import os
import shutil
from datetime import datetime, timezone

from dotenv import load_dotenv

from app.modules.audiodataset.models import Audio, AudioDataset, AudioMetaData
from app.modules.auth.models import User
from app.modules.dataset.models import Author, DSMetaData, PublicationType
from app.modules.hubfile.models import Hubfile
from core.seeders.BaseSeeder import BaseSeeder


class AudioDatasetSeeder(BaseSeeder):
    priority = 3

    def _checksum_and_size(self, file_path: str) -> tuple[str, int]:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest(), os.path.getsize(file_path)

    def run(self):
        load_dotenv()

        user = User.query.filter_by(email="user1@example.com").first()
        if not user:
            raise Exception("User for seeding audio datasets not found. Please seed users first.")

        working_dir = os.getenv("WORKING_DIR", "")
        src_folder = os.path.join(working_dir, "app", "modules", "audiodataset", "songs_examples")

        if not os.path.isdir(src_folder):
            raise Exception(f"Audio samples folder not found: {src_folder}")

        dataset_definitions = [
            {
                "title": "SongHub Sample Pack Vol. 1",
                "description": "Demo collection with corporate and ambient tracks bundled for audio dataset testing.",
                "tags": "audio,example,songhub,samples",
                "doi": "10.9999/songhub-audio-1",
                "deposition_id": 501,
                "tracks": [
                    {
                        "filename": "positive-emotive-corporate-business-advertising-music-252194.mp3",
                        "title": "Corporate Uplift",
                        "description": "Bright corporate soundtrack suited for ads and onboarding demos.",
                    },
                    {
                        "filename": "serious-dark-ambient-atmosphere-116115.mp3",
                        "title": "Dark Atmosphere",
                        "description": "Moody ambient bed for suspenseful or introspective sections.",
                    },
                ],
            },
            {
                "title": "SongHub Sample Pack Vol. 2",
                "description": "Second batch mixing emotive ad-libs and latin grooves to exercise audio flows.",
                "tags": "audio,example,songhub,samples",
                "doi": "10.9999/songhub-audio-2",
                "deposition_id": 502,
                "tracks": [
                    {
                        "filename": "emotional-ad-libs-267170.mp3",
                        "title": "Emotional Ad Libs",
                        "description": "Layered vocal ad-libs with soft backing for melodic testing.",
                    },
                    {
                        "filename": "sneaky-ways-latin-207042.mp3",
                        "title": "Sneaky Latin Groove",
                        "description": "Playful latin rhythm with bright brass and percussion hits.",
                    },
                ],
            },
        ]

        for dataset_def in dataset_definitions:
            existing_dataset = (
                AudioDataset.query.join(DSMetaData).filter(DSMetaData.title == dataset_def["title"]).first()
            )
            if existing_dataset:
                continue

            ds_meta = DSMetaData(
                deposition_id=dataset_def["deposition_id"],
                title=dataset_def["title"],
                description=dataset_def["description"],
                publication_type=PublicationType.OTHER,
                publication_doi="",
                dataset_doi=dataset_def["doi"],
                tags=dataset_def["tags"],
            )
            self.db.session.add(ds_meta)
            self.db.session.flush()

            ds_author = Author(
                name="SongHub Audio Team",
                affiliation="SongHub Samples",
                orcid="",
                ds_meta_data_id=ds_meta.id,
            )
            self.db.session.add(ds_author)

            dataset = AudioDataset(
                user_id=user.id,
                ds_meta_data_id=ds_meta.id,
                created_at=datetime.now(timezone.utc),
            )
            self.db.session.add(dataset)
            self.db.session.flush()

            dest_folder = os.path.join(working_dir, "uploads", f"user_{user.id}", f"dataset_{dataset.id}")
            os.makedirs(dest_folder, exist_ok=True)

            for track in dataset_def["tracks"]:
                source_path = os.path.join(src_folder, track["filename"])
                if not os.path.isfile(source_path):
                    raise Exception(f"Missing source audio file for seeding: {track['filename']}")

                audio_metadata = AudioMetaData(
                    filename=track["filename"],
                    title=track["title"],
                    description=track["description"],
                    publication_type=PublicationType.NONE,
                    publication_doi="",
                    tags=dataset_def["tags"],
                )
                self.db.session.add(audio_metadata)
                self.db.session.flush()

                audio_author = Author(
                    name="SongHub Audio Team",
                    affiliation="SongHub Samples",
                    orcid="",
                    audio_meta_data_id=audio_metadata.id,
                )
                self.db.session.add(audio_author)

                audio = Audio(data_set_id=dataset.id, audio_meta_data_id=audio_metadata.id)
                self.db.session.add(audio)
                self.db.session.flush()

                dest_path = os.path.join(dest_folder, track["filename"])
                shutil.copy(source_path, dest_path)

                checksum, size = self._checksum_and_size(dest_path)
                file_entry = Hubfile(name=track["filename"], checksum=checksum, size=size, audio_id=audio.id)
                self.db.session.add(file_entry)

            self.db.session.commit()
