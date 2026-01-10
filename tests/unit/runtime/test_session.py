"""
Unit tests for Session lifecycle.
"""

import pytest
from datetime import datetime
from symphainy_platform.runtime.session import Session


@pytest.mark.unit
@pytest.mark.runtime
class TestSession:
    """Test Session lifecycle."""
    
    def test_create_session(self):
        """Test session creation."""
        session = Session.create(
            tenant_id="test_tenant",
            user_id="test_user",
            context={"key": "value"}
        )
        
        assert session.tenant_id == "test_tenant"
        assert session.user_id == "test_user"
        assert session.context == {"key": "value"}
        assert session.session_id is not None
        assert session.created_at is not None
        assert session.active_sagas == []
    
    def test_session_to_dict(self):
        """Test session serialization."""
        session = Session.create(
            tenant_id="test_tenant",
            user_id="test_user"
        )
        
        data = session.to_dict()
        assert data["tenant_id"] == "test_tenant"
        assert data["user_id"] == "test_user"
        assert "session_id" in data
        assert "created_at" in data
    
    def test_add_saga(self):
        """Test adding saga to session."""
        session = Session.create(
            tenant_id="test_tenant",
            user_id="test_user"
        )
        
        session.add_saga("saga_123")
        assert "saga_123" in session.active_sagas
        assert session.updated_at is not None
    
    def test_remove_saga(self):
        """Test removing saga from session."""
        session = Session.create(
            tenant_id="test_tenant",
            user_id="test_user"
        )
        
        session.add_saga("saga_123")
        session.remove_saga("saga_123")
        assert "saga_123" not in session.active_sagas
    
    def test_update_context(self):
        """Test updating session context."""
        session = Session.create(
            tenant_id="test_tenant",
            user_id="test_user",
            context={"key1": "value1"}
        )
        
        session.update_context({"key2": "value2"})
        assert session.context["key1"] == "value1"
        assert session.context["key2"] == "value2"
