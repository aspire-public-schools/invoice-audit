# routes/coupa.py
import os
import pickle
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from coupa.invoices import get_invoice_details
from coupa.attachments import download_all_invoice_attachments, download_invoice_attachment, download_multiple_invoices, get_invoice_attachments
from coupa.utils import extract_filename_from_url, sanitize_filename, log
from coupa.auth import get_access_token



router = APIRouter()

class CoupaRunRequest(BaseModel):
    invoice_ids: List[str]
    run_name: str


@router.post("/run")
def run_coupa_batch(req: CoupaRunRequest):
    invoice_ids = req.invoice_ids
    run_name = sanitize_filename(req.run_name)

    # Set up folders
    run_folder = os.path.join("audit_runs", run_name)
    attachments_folder = os.path.join(run_folder, "attachments")
    os.makedirs(attachments_folder, exist_ok=True)

    # Fetch and pickle invoice metadata
    invoice_data = []
    access_token = get_access_token()
    if not access_token:
        raise HTTPException(status_code=500, detail="Unable to acquire Coupa access token")

    for idx, invoice_id in enumerate(invoice_ids, start=1):
        log(f"[{idx}/{len(invoice_ids)}] Fetching invoice: {invoice_id}")
        response = get_invoice_details(invoice_id, access_token)

        if response.status_code != 200:
            log(f"❌ Failed to retrieve invoice {invoice_id}", "error")
            continue

        try:
            data = response.json()
            invoice_data.append(data)
        except Exception as e:
            log(f"⚠️ Error parsing JSON for invoice {invoice_id}: {e}", "warn")

        # Download attachments
        attach_response = get_invoice_attachments(invoice_id, access_token)
        if attach_response.status_code != 200:
            log(f"❌ Failed to retrieve attachments for invoice {invoice_id}", "error")
            continue

        for attachment in attach_response.json():
            attachment_id = attachment.get("id")
            file_url = attachment.get("file-url") or attachment.get("file")
            if not attachment_id or not file_url:
                log(f"Missing ID or URL for invoice {invoice_id} attachment", "warn")
                continue

            original_filename = extract_filename_from_url(file_url)
            try:
                download_invoice_attachment(
                    invoice_id,
                    attachment_id,
                    access_token,
                    download_folder=attachments_folder,
                    original_filename=original_filename
                )
            except Exception as e:
                log(f"❌ Error downloading attachment {attachment_id}: {e}", "error")

    # Save invoice metadata
    pickle_path = os.path.join(run_folder, "invoice_details.pkl")
    with open(pickle_path, "wb") as f:
        pickle.dump(invoice_data, f)

    return {
        "message": "Run complete",
        "invoice_count": len(invoice_data),
        "output_pickle": pickle_path,
        "attachments_folder": attachments_folder,
        "run_name": run_name
    }

@router.post("/invoice/{invoice_id}")
def fetch_invoice(invoice_id: str):
    response = get_invoice_details(invoice_id)
    return response.json()

@router.post("/invoice/{invoice_id}/attachments")
def fetch_attachments(invoice_id: str):
    download_all_invoice_attachments(invoice_id)
    return {"message": f"Attachments downloaded for invoice {invoice_id}"}

class BulkDownloadRequest(BaseModel):
    invoice_ids: List[str]
    download_folder: str = "downloads"
    log_file: str = "download_log.txt"

@router.post("/invoices/download")
def bulk_download_invoices(req: BulkDownloadRequest):
    download_multiple_invoices(
        req.invoice_ids,
        download_folder=req.download_folder,
        log_file=req.log_file
    )
    return {
        "message": f"Downloaded attachments for {len(req.invoice_ids)} invoice(s).",
        "log_file": req.log_file
    }
