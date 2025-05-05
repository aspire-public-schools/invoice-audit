from mistral import processors
from unittest.mock import patch
import tempfile
import os

@patch("mistral.processors.upload_pdf")
@patch("mistral.processors.ask_pdf_questions")
def test_process_all_pdfs(mock_prompt, mock_upload, tmp_path):
    mock_upload.return_value = "https://fake.url"
    mock_prompt.return_value = "Fake extracted table"

    # Create some fake PDFs
    for i in range(3):
        f = tmp_path / f"invoice_{i}.pdf"
        f.write_bytes(b"%PDF-1.4 dummy")

    output_file = tmp_path / "results.txt"
    log_file = tmp_path / "done.log"

    processors.process_all_pdfs(
        download_folder=str(tmp_path),
        output_file=str(output_file),
        log_file=str(log_file),
        max_chunk_size=2
    )

    with open(output_file, "r") as f:
        assert "Fake extracted table" in f.read()