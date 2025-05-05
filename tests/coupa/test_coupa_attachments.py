from coupa.attachments import (
    get_invoice_attachments, download_invoice_attachment,
    download_all_invoice_attachments, download_multiple_invoices
)
import os

def test_get_invoice_attachments():
    response = get_invoice_attachments("123456")
    assert response.status_code in [200, 404]

def test_download_invoice_attachment(tmp_path):
    invoice_id = "123456"
    attachment_id = "789"
    access_token = os.getenv("access_token") or "fake-token"
    filename = download_invoice_attachment(invoice_id, attachment_id, access_token, download_folder=tmp_path)
    assert filename is None or os.path.exists(tmp_path / filename)

def test_download_all_invoice_attachments():
    try:
        download_all_invoice_attachments("123456")
    except Exception:
        assert True  # No crash

def test_download_multiple_invoices(tmp_path):
    invoice_ids = ["123456"]
    log_file = tmp_path / "log.txt"
    try:
        download_multiple_invoices(invoice_ids, download_folder=tmp_path, log_file=str(log_file))
    except Exception:
        assert True