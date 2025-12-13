from app.modules.featuremodel.models import UVLDataset
from app import db


def test_uvl_dataset_creation(test_client):
    # Setup
    ds_meta = DSMetaData(
        title="Test UVL Dataset",
        description="Desc",
        publication_type=PublicationType.NONE
    )
    db.session.add(ds_meta)
    db.session.commit()

    # Create UVLDataset
    uvl_ds = UVLDataset(user_id=1, ds_meta_data_id=ds_meta.id)
    db.session.add(uvl_ds)
    db.session.commit()

    # Verify ID
    assert uvl_ds.id is not None
    assert uvl_ds.dataset_type == 'uvl_dataset'

    # Verify Polymorphic Query
    ds = DataSet.query.get(uvl_ds.id)
    assert isinstance(ds, UVLDataset)
    assert ds.dataset_type == 'uvl_dataset'
    
    # Verify Relationship
    assert hasattr(ds, 'feature_models')
    
    # Cleanup
    db.session.delete(uvl_ds)  # Should cascade if set up correctly
    db.session.delete(ds_meta)
    db.session.commit()


def test_base_dataset_creation(test_client):
    # Setup
    ds_meta = DSMetaData(
        title="Test Base Dataset",
        description="Desc",
        publication_type=PublicationType.NONE
    )
    db.session.add(ds_meta)
    db.session.commit()

    # Create Base DataSet
    ds = DataSet(user_id=1, ds_meta_data_id=ds_meta.id)
    db.session.add(ds)
    db.session.commit()

    # Verify
    assert ds.dataset_type == 'dataset'
    fetched_ds = DataSet.query.get(ds.id)
    assert not isinstance(fetched_ds, UVLDataset)
    assert isinstance(fetched_ds, DataSet)
    
    # Check that it implies no files
    assert fetched_ds.files() == []
    assert fetched_ds.get_files_count() == 0

    # Cleanup
    db.session.delete(ds)
    db.session.delete(ds_meta)
    db.session.commit()
