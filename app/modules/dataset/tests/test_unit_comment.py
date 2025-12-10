import pytest
from datetime import datetime
from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DatasetComment

def _get_first_dataset_and_user():
    """Return (dataset, user) from DB or (None, None) if missing."""
    dataset = db.session.query(DataSet).first()
    user = db.session.query(User).first()
    return dataset, user

def test_comment_creation(test_database_poblated):
    """Test that a comment can be created and persisted."""
    dataset, user = _get_first_dataset_and_user()
    if not dataset or not user:
        pytest.skip("No dataset or user seeded")

    content = "This is a test comment"
    comment = DatasetComment(dataset_id=dataset.id, user_id=user.id, content=content)
    db.session.add(comment)
    db.session.commit()

    assert comment.id is not None
    assert comment.content == content
    assert comment.dataset_id == dataset.id
    assert comment.user_id == user.id
    assert comment.is_deleted is False
    assert comment.created_at is not None

def test_comment_relationships(test_database_poblated):
    """Test that relationships (author, dataset) work correctly."""
    dataset, user = _get_first_dataset_and_user()
    if not dataset or not user:
        pytest.skip("No dataset or user seeded")

    comment = DatasetComment(dataset_id=dataset.id, user_id=user.id, content="Relationship test")
    db.session.add(comment)
    db.session.commit()

    # Reload to ensure relationships are loaded
    retrieved_comment = db.session.query(DatasetComment).get(comment.id)
    
    assert retrieved_comment.author == user
    assert retrieved_comment.dataset == dataset
    assert retrieved_comment in dataset.comments

def test_comment_update(test_database_poblated):
    """Test that updating a comment updates the updated_at field."""
    dataset, user = _get_first_dataset_and_user()
    if not dataset or not user:
        pytest.skip("No dataset or user seeded")

    comment = DatasetComment(dataset_id=dataset.id, user_id=user.id, content="Original content")
    db.session.add(comment)
    db.session.commit()

    original_updated_at = comment.updated_at
    
    # Update content
    comment.content = "Updated content"
    db.session.commit()
    
    # Check if content changed
    assert comment.content == "Updated content"
    
    # Note: updated_at logic depends on the model definition.
    # The model defines: updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    # We may need to check if it's not None (it starts as None usually unless default is set, which it isn't for created_at).
    # Actually, created_at is set on creation. updated_at is nullable=True.
    assert comment.updated_at is not None

def test_comment_soft_delete(test_database_poblated):
    """Test soft deletion logic."""
    dataset, user = _get_first_dataset_and_user()
    if not dataset or not user:
        pytest.skip("No dataset or user seeded")

    comment = DatasetComment(dataset_id=dataset.id, user_id=user.id, content="To be deleted")
    db.session.add(comment)
    db.session.commit()

    # "Soft delete"
    comment.is_deleted = True
    comment.deleted_at = datetime.utcnow()
    comment.deleted_by = user.id
    db.session.commit()

    assert comment.is_deleted is True
    assert comment.deleted_at is not None
    assert comment.deleter == user
    
    # It should still exist in DB
    assert db.session.query(DatasetComment).get(comment.id) is not None

def test_comment_to_dict(test_database_poblated):
    """Test to_dict method behavior for normal and deleted comments."""
    dataset, user = _get_first_dataset_and_user()
    if not dataset or not user:
        pytest.skip("No dataset or user seeded")

    # Normal comment
    comment = DatasetComment(dataset_id=dataset.id, user_id=user.id, content="Dict test")
    db.session.add(comment)
    db.session.commit()

    data = comment.to_dict()
    assert data['content'] == "Dict test"
    assert data['is_deleted'] is False
    assert data['author']['id'] == user.id

    # Deleted comment
    comment.is_deleted = True
    db.session.commit()
    
    data_deleted = comment.to_dict()
    assert data_deleted['content'] == "[Comment deleted]"
    assert data_deleted['is_deleted'] is True
    # The implementation of to_dict in models.py returns None for author if deleted
    # 196: 'author': { ... } if self.author and not self.is_deleted else None
    assert data_deleted['author'] is None
