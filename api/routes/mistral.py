from fastapi import APIRouter, HTTPException
from mistral.processors import process_all_pdfs
from mistral.processors import process_grouped_invoices
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


@router.post("/process-run")
def process_ocr_run(req: ProcessRunRequest):
    run_name = sanitize_filename(req.run_name)
    attachments_dir = os.path.join("audit_runs", run_name, "attachments")
    output_file = os.path.join("audit_runs", run_name, "ocr_output.txt")

    if not os.path.exists(attachments_dir):
        raise HTTPException(status_code=404, detail=f"Attachments folder for run '{run_name}' not found.")

    process_grouped_invoices(
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
