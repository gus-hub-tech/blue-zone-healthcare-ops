"""Health check endpoint tests"""
import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test basic health check endpoint"""
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_db_health_check(client: TestClient):
    """Test database health check endpoint"""
    response = client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
