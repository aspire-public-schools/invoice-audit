import os
import requests
from .auth import get_access_token
from .utils import sanitize_filename, extract_filename_from_url, log

def get_invoice_attachments(invoice_id, access_token=None):
    if access_token is None:
        access_token = get_access_token()
        if not access_token:
            raise ValueError("Unable to obtain a valid access token.")

    base_url = os.getenv("URL")
    endpoint = f"{base_url}/api/invoices/{invoice_id}/attachments"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code != 200:
        log(f"Failed to get attachments for invoice {invoice_id}. Status Code: {response.status_code}", "error")
        log(response.text, "error")
    else:
        log(f"Successfully retrieved attachments for invoice {invoice_id}.", "success")

    return response

def download_invoice_attachment(invoice_id, attachment_id, access_token, download_folder="downloads", original_filename=None):
    base_url = os.getenv("URL")
    endpoint = f"{base_url}/api/invoices/{invoice_id}/attachments/{attachment_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        if original_filename:
            original_filename = sanitize_filename(original_filename)
        else:
            original_filename = f"attachment_{attachment_id}.bin"

        final_filename = f"invoice_{invoice_id}_attachment_{attachment_id}_{original_filename}"
        os.makedirs(download_folder, exist_ok=True)
        filepath = os.path.join(download_folder, final_filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        log(f"Downloaded: {final_filename}", "success")
        return final_filename
    else:
        log(f"Failed to download attachment {attachment_id} (Invoice: {invoice_id})", "error")
        log(response.text, "error")
        return None

def download_all_invoice_attachments(invoice_id, download_folder="downloads"):
    response = get_invoice_attachments(invoice_id)
    if response.status_code == 200:
        attachments = response.json()
        if not attachments:
            log(f"No attachments found for invoice {invoice_id}", "warn")
            return
        access_token = get_access_token()
        for attachment in attachments:
            attachment_id = attachment.get("id")
            file_url = attachment.get("file-url") or attachment.get("file")
            
            if attachment_id and file_url:
                original_filename = extract_filename_from_url(file_url)
                download_invoice_attachment(
                    invoice_id, attachment_id, access_token,
                    download_folder, original_filename
                )
            else:
                log("Attachment missing 'id' or 'file-url'.", "warn")
    else:
        log(f"Could not retrieve attachments for invoice {invoice_id}. Status code: {response.status_code}", "error")

def download_multiple_invoices(invoice_ids, download_folder="downloads", log_file="download_log.txt"):
    os.makedirs(download_folder, exist_ok=True)

    with open(log_file, "w", encoding="utf-8") as log_file_writer:
        log_file_writer.write("InvoiceID\tAttachmentID\tFilename\n")

        access_token = get_access_token()
        for invoice_id in invoice_ids:
            log(f"Processing invoice: {invoice_id}", "info")
            response = get_invoice_attachments(invoice_id, access_token)

            if response.status_code != 200:
                log(f"Failed to retrieve attachments for invoice {invoice_id}. Status: {response.status_code}", "error")
                continue

            attachments = response.json()
            if not attachments:
                log(f"No attachments found for invoice {invoice_id}", "warn")
                continue

            for attachment in attachments:
                attachment_id = attachment.get("id")
                file_url = attachment.get("file-url") or attachment.get("file")

                if not attachment_id or not file_url:
                    log(f"Missing attachment ID or file URL for invoice {invoice_id}", "warn")
                    continue

                original_filename = extract_filename_from_url(file_url)
                log(f"Downloading attachment {attachment_id} ({original_filename}) for invoice {invoice_id}", "info")
                try:
                    saved_filename = download_invoice_attachment(
                        invoice_id, attachment_id, access_token,
                        download_folder, original_filename
                    )
                    if saved_filename:
                        log_file_writer.write(f"{invoice_id}\t{attachment_id}\t{saved_filename}\n")
                        log_file_writer.flush()
                except Exception as e:
                    log(f"Error downloading attachment {attachment_id}: {e}", "error")

    log(f"All done! Download log saved to: {log_file}", "success")