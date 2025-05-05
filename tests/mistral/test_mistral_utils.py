from mistral.utils import extract_invoice_id, chunked

def test_extract_invoice_id():
    assert extract_invoice_id("invoice_123456_attachment_789.pdf") == "123456"
    assert extract_invoice_id("not_invoice_file.pdf") is None

def test_chunked():
    data = list(range(10))
    chunks = list(chunked(data, 3))
    assert chunks == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
