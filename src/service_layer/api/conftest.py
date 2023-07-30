import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def api_client():
    return TestClient()

