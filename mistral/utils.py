import os
import re
import urllib.parse
from typing import List, Generator

def extract_invoice_id(filename: str) -> str:
    """
    Extracts invoice ID from filenames like 'invoice_123456_attachment_789.pdf'.
    Returns the invoice ID or None if not found.
    """
    parts = filename.split("_")
    if len(parts) >= 2 and parts[0].lower() == "invoice":
        return parts[1]
    return None


def extract_filename_from_url(url: str) -> str:
    """
    Extract the filename from a given URL path.
    """
    return os.path.basename(urllib.parse.urlparse(url).path)


def save_llm_table_to_file(llm_response: str, filename: str = "output_table.txt") -> None:
    """
    Saves triple-backtick-wrapped content from a response to a file.
    """
    match = re.search(r"```(.*?)```", llm_response, re.DOTALL)
    if match:
        table_data = match.group(1).strip()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(table_data)
        print(f"✅ Table saved to {filename}")
    else:
        print("❌ No table data found in the response.")


def list_files_with_size(root_folder: str, output_file: str) -> None:
    """
    Writes a list of all files in a folder (recursively) with size info.
    """
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write("FullPath\tFilename\tSizeBytes\n")
        for dirpath, _, filenames in os.walk(root_folder):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    size = os.path.getsize(file_path)
                    out_file.write(f"{file_path}\t{filename}\t{size}\n")
                except Exception as e:
                    print(f"❌ Could not process file: {file_path} — {e}")
    print(f"📄 File listing saved to: {output_file}")

def chunked(iterable: List, size: int) -> Generator[List, None, None]:
    """
    Yield successive chunks from a list.
    """
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]