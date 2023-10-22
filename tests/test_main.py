from fastapi.testclient import TestClient

from app.main import app
from app.models.restaurant import Restaurant

client = TestClient(app)

def test():
    assert True
