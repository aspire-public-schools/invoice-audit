import re
import os
import urllib.parse

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def extract_filename_from_url(url):
    return os.path.basename(urllib.parse.urlparse(url).path)

def log(msg, level="info"):
    print(f"[{level.upper()}] {msg}")