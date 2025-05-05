import pytest
from mistral import uploader
from unittest.mock import MagicMock, patch

@patch("mistral.uploader.client.files.upload")
@patch("mistral.uploader.client.files.get_signed_url")
def test_upload_pdf(mock_get_url, mock_upload, tmp_path):
    # Setup mock return values
    mock_upload.return_value.id = "mock_file_id"
    mock_get_url.return_value.url = "https://fake.url/test.pdf"

    # Create a temp PDF
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"%PDF-1.4 fake content")

    url = uploader.upload_pdf(str(test_file))
    assert url == "https://fake.url/test.pdf"
