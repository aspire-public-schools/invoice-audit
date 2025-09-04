import re
import os
import urllib.parse

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def extract_filename_from_url(url):
    return os.path.basename(urllib.parse.urlparse(url).path)

def log(msg, level="info"):
    print(f"[{level.upper()}] {msg}")

def parse_invoice_ids(invoice_ids):
    """
    Parse invoice IDs from a list that may contain comma-separated values.
    Handles Power Automate sending comma-separated invoice IDs as single strings.
    
    Args:
        invoice_ids: List of strings that may contain comma-separated invoice IDs
        
    Returns:
        List of individual invoice ID strings with whitespace stripped
    """
    parsed_ids = []
    for id_string in invoice_ids:
        # Split by comma and strip whitespace from each ID
        split_ids = [id.strip() for id in id_string.split(',') if id.strip()]
        parsed_ids.extend(split_ids)
    return parsed_ids