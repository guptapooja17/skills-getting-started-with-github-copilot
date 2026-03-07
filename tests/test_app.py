
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from src.app import app


@pytest.mark.asyncio
async def test_get_activities():
    # Arrange
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.get("/activities")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


@pytest.mark.asyncio
async def test_signup_and_unregister():
    # Arrange
    test_email = "testuser@mergington.edu"
    activity = "Chess Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act: Sign up
        signup_resp = await ac.post(f"/activities/{activity}/signup?email={test_email}")
        # Assert
        assert signup_resp.status_code == status.HTTP_200_OK
        assert f"Signed up {test_email}" in signup_resp.json()["message"]

        # Act: Duplicate signup
        dup_resp = await ac.post(f"/activities/{activity}/signup?email={test_email}")
        # Assert
        assert dup_resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in dup_resp.json()["detail"].lower()

        # Act: Unregister
        unreg_resp = await ac.post(f"/activities/{activity}/unregister?email={test_email}")
        # Assert
        assert unreg_resp.status_code == status.HTTP_200_OK
        assert f"Unregistered {test_email}" in unreg_resp.json()["message"]

        # Act: Unregister again (should fail)
        unreg_again = await ac.post(f"/activities/{activity}/unregister?email={test_email}")
        # Assert
        assert unreg_again.status_code == status.HTTP_400_BAD_REQUEST
        assert "not registered" in unreg_again.json()["detail"].lower()


@pytest.mark.asyncio
async def test_activity_not_found():
    # Arrange
    test_email = "ghost@mergington.edu"
    fake_activity = "Nonexistent Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        resp = await ac.post(f"/activities/{fake_activity}/signup?email={test_email}")
        # Assert
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in resp.json()["detail"].lower()

        # Act
        resp2 = await ac.post(f"/activities/{fake_activity}/unregister?email={test_email}")
        # Assert
        assert resp2.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in resp2.json()["detail"].lower()
