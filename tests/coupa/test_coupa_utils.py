from coupa.utils import sanitize_filename, extract_filename_from_url, log

def test_sanitize_filename():
    assert sanitize_filename("bad:file/name.pdf") == "bad_file_name.pdf"

def test_extract_filename_from_url():
    url = "https://example.com/path/to/file-name.pdf"
    assert extract_filename_from_url(url) == "file-name.pdf"

def test_log(capsys):
    log("Hello World", "info")
    captured = capsys.readouterr()
    assert "[INFO] Hello World" in captured.out