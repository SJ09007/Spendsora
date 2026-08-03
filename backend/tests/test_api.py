import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.categorization_service import categorization_service

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "ExpenseSense AI"

def test_nlp_categorizer_parsing():
    parsed1 = categorization_service.parse_and_categorize("80 chai")
    assert parsed1["amount"] == 80.0
    assert parsed1["category"] == "Food"

    parsed2 = categorization_service.parse_and_categorize("350 petrol")
    assert parsed2["amount"] == 350.0
    assert parsed2["category"] == "Transport"

    parsed3 = categorization_service.parse_and_categorize("1200 Amazon")
    assert parsed3["amount"] == 1200.0
    assert parsed3["category"] == "Shopping"

    parsed4 = categorization_service.parse_and_categorize("499 Netflix")
    assert parsed4["amount"] == 499.0
    assert parsed4["category"] == "Subscriptions"

def test_user_registration_and_login():
    test_email = f"test_{pytest.__name__}@expensesense.com"
    reg_data = {
        "email": test_email,
        "password": "securepassword123",
        "full_name": "Test Engineer",
        "currency": "₹",
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]

    # Test authenticated GET /me
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == test_email
