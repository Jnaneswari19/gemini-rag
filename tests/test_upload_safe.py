import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_txt(tmp_path):
    """Upload a simple text file and check response structure."""
    test_file = tmp_path / "file1.txt"
    test_file.write_text("Hello Gemini RAG system")

    with open(test_file, "rb") as f:
        response = client.post("/upload", files={"file": f})

    assert response.status_code == 200
    data = response.json()

    # Check for required fields
    assert "document_id" in data
    assert data["filename"] == "file1.txt"
    assert isinstance(data["message"], str)  # just ensure it's a string
