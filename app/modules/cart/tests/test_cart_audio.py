import io
import os
import zipfile

from app import db
from app.modules.audiodataset.models import Audio, AudioDataset, AudioMetaData
from app.modules.auth.models import User
from app.modules.dataset.models import DSMetaData, PublicationType
from app.modules.hubfile.models import Hubfile


def test_cart_audio_flow(test_client):
    """
    Test the full flow of adding audio to cart and downloading it.
    """
    # 1. Setup User
    user = User(email="audio_cart_test@example.com", password="password")
    db.session.add(user)
    db.session.commit()

    # 2. Setup AudioDataset and Audio
    ds_meta = DSMetaData(
        title="Audio Test DS", description="Desc", publication_type=PublicationType.OTHER, deposition_id=99999
    )
    db.session.add(ds_meta)
    db.session.commit()

    ds = AudioDataset(user_id=user.id, ds_meta_data_id=ds_meta.id)
    db.session.add(ds)
    db.session.commit()

    # Create fake audio file on disk
    upload_folder = f"uploads/user_{user.id}/dataset_{ds.id}"
    os.makedirs(upload_folder, exist_ok=True)
    with open(os.path.join(upload_folder, "test_track.mp3"), "wb") as f:
        f.write(b"fake audio content")

    audio_meta = AudioMetaData(
        filename="test_track.mp3", title="Test Track", description="Desc", publication_type=PublicationType.OTHER
    )
    db.session.add(audio_meta)
    db.session.commit()

    audio = Audio(data_set_id=ds.id, audio_meta_data_id=audio_meta.id)
    db.session.add(audio)
    db.session.commit()

    hubfile = Hubfile(name="test_track.mp3", size=100, checksum="123", audio_id=audio.id)
    db.session.add(hubfile)
    db.session.commit()

    login_resp = test_client.post("/login", data={"email": "audio_cart_test@example.com", "password": "password"})
    assert login_resp.status_code == 302  # Successful login redirects

    # Add to cart via API
    resp = test_client.post(f"/cart/add/audio/{audio.id}")
    assert resp.status_code == 200
    assert resp.json["success"] is True

    # Verify count
    resp = test_client.get("/cart/count")
    assert resp.json["count"] == 1

    # Verify Cart Page Rendering (this catches Jinja2 errors)
    resp = test_client.get("/cart")
    assert resp.status_code == 200
    assert b"My Cart" in resp.data

    # 4. Verify Service Internal State
    with test_client.application.app_context():
        pass

    # 5. Test Download
    resp = test_client.get("/cart/download")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/zip"

    # Verify zip content
    zip_buffer = io.BytesIO(resp.data)
    with zipfile.ZipFile(zip_buffer) as zf:
        # Check if file exists in zip (structure: dataset_name/filename)
        # dataset_name should be sanitized "Audio Test DS" -> "Audio_Test_DS"
        expected_path = "Audio Test DS/test_track.mp3"
        assert expected_path in zf.namelist()

    # 6. Test Remove
    resp = test_client.post("/cart/clear")
    assert resp.status_code == 200

    resp = test_client.get("/cart/count")
    assert resp.json["count"] == 0
