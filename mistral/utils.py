import os
import re
import urllib.parse
import json
from typing import List, Generator, Dict, Any

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


def parse_json_ocr_output(content: str) -> List[Dict[str, Any]]:
    """
    Parse OCR output file containing JSON data from multiple files.
    Returns a list of dictionaries with filename, JSON data, and notes.
    """
    results = []
    
    for section in content.split('=' * 60):
        if not (section := section.strip()):
            continue
            
        lines = section.split('\n', 1)
        if len(lines) < 2:
            continue
            
        filename = lines[0].replace('File: ', '')
        file_content = lines[1].strip()
        
        # Extract JSON and notes separately
        json_data = extract_json_from_content(file_content)
        notes = extract_notes_from_content(file_content)
        
        if json_data:
            result = {"filename": filename, **json_data}
            result["notes"] = notes  # Always include notes, even if empty
            results.append(result)
    
    return results


def extract_json_from_content(content: str) -> Dict[str, Any]:
    """
    Extract and parse JSON data from content with markdown formatting.
    Returns parsed JSON data or error information.
    """
    # Find JSON code block
    if '```json' in content:
        start = content.find('```json') + 7
        end = content.find('```', start)
        if end != -1:
            json_str = content[start:end].strip()
    else:
        # Fallback: find JSON between braces
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end > start:
            json_str = content[start:end + 1]
        else:
            return {"error": "No JSON found", "raw_content": content}
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}", "raw_content": json_str}


def extract_notes_from_content(content: str) -> str:
    """
    Extract notes from content (everything after JSON).
    Returns notes as string, empty string if no notes found.
    """
    # Find JSON code block and get content after it
    if '```json' in content:
        start = content.find('```json') + 7
        end = content.find('```', start)
        if end != -1:
            return content[end + 3:].strip()
    
    # Fallback: find JSON between braces and get content after it
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end > start:
        return content[end + 1:].strip()
    
    return ""  # No JSON found, so no notes