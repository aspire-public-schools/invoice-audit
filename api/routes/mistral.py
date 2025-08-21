from fastapi import APIRouter, HTTPException
from mistral.processors import process_all_pdfs
from mistral.processors import process_grouped_invoices
from mistral.utils import parse_json_ocr_output
from pydantic import BaseModel
from coupa.utils import sanitize_filename
import os

router = APIRouter()

@router.post("/process")
def run_mistral_ocr(folder: str = "downloads", output_file: str = "results.txt"):
    process_all_pdfs(folder, output_file)
    return {"message": "Mistral OCR processing complete."}

class ProcessRunRequest(BaseModel):
    run_name: str
    chunk_size: int = 100
    cooldown_seconds: int = 0
    prompt_text: str | None = None


class GetResultsRequest(BaseModel):
    run_name: str


@router.post("/process-run")
def process_ocr_run(req: ProcessRunRequest):
    run_name = sanitize_filename(req.run_name)
    attachments_dir = os.path.join("audit_runs", run_name, "attachments")
    output_file = os.path.join("audit_runs", run_name, "ocr_output.txt")

    if not os.path.exists(attachments_dir):
        raise HTTPException(status_code=404, detail=f"Attachments folder for run '{run_name}' not found.")

    process_all_pdfs(
        download_folder=attachments_dir,
        output_file=output_file,
        max_chunk_size=req.chunk_size,
        cooldown_seconds=req.cooldown_seconds,
        prompt_text=req.prompt_text  # ✅ now dynamic!
    )

    return {
        "message": "OCR processing completed",
        "output_file": output_file,
        "run_name": run_name
    }


@router.get("/results")
def get_ocr_results(req: GetResultsRequest):
    """
    Retrieve and parse the OCR results for a specific run.
    Returns the parsed JSON content from the output file.
    """
    # Validate run_name to prevent path traversal
    sanitized_run_name = sanitize_filename(req.run_name)
    if sanitized_run_name != req.run_name:
        raise HTTPException(status_code=400, detail="Invalid run name")
    
    output_file = os.path.join("audit_runs", sanitized_run_name, "ocr_output.txt")
    
    if not os.path.exists(output_file):
        raise HTTPException(
            status_code=404, 
            detail=f"Results not found for run '{req.run_name}'. The processing may not have completed yet."
        )
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            results = parse_json_ocr_output(f.read())
        
        return {
            "run_name": req.run_name,
            "file_path": output_file,
            "total_files": len(results),
            "results": results
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=500, detail="Error reading file encoding")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading results: {str(e)}")
