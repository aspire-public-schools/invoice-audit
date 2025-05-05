import os
import glob
import time
from mistral.uploader import upload_pdf
from mistral.prompts import ask_pdf_questions
from mistral.utils import extract_invoice_id, save_llm_table_to_file, chunked
from collections import defaultdict
from mistral.constants import ALLOWED_EXTENSIONS


def process_all_pdfs(
    download_folder,
    output_file,
    log_file="completed_files.txt",
    prompt_text=None,
    max_chunk_size=100,
    cooldown_seconds=0
):
    """
    Upload and process all PDFs in a folder in chunks (to respect rate limits).
    """
    prompt_text = prompt_text or "Give me the table in this file in a tab separated format"

    pdf_files = [
    f for f in glob.glob(os.path.join(download_folder, "*"))
    if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ]

    completed_files = set()
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            completed_files = set(line.strip() for line in f if line.strip())

    to_process = [f for f in pdf_files if os.path.basename(f) not in completed_files]
    chunk_batches = list(chunked(to_process, max_chunk_size))

    print(f"📦 Processing {len(to_process)} files in {len(chunk_batches)} chunks of max {max_chunk_size}...")

    with open(output_file, "a", encoding="utf-8") as out_file, \
         open(log_file, "a", encoding="utf-8") as log:
        for chunk_idx, chunk in enumerate(chunk_batches, start=1):
            print(f"\n🚀 Chunk {chunk_idx}/{len(chunk_batches)}: {len(chunk)} file(s)")

            for idx, pdf_path in enumerate(chunk, start=1):
                file_name = os.path.basename(pdf_path)
                try:
                    print(f"[{idx}] 🔄 Uploading: {file_name}")
                    url = upload_pdf(pdf_path)

                    print(f"🤖 Asking LLM: {prompt_text}")
                    response = ask_pdf_questions(prompt_text, url)

                    out_file.write(f"File: {file_name}\n{response}\n{'='*60}\n")
                    log.write(f"{file_name}\n")
                    log.flush()

                    print(f"✅ Done: {file_name}")
                except Exception as e:
                    print(f"❌ Error processing {file_name}: {e}")

            if cooldown_seconds > 0 and chunk_idx < len(chunk_batches):
                print(f"🕒 Cooling down for {cooldown_seconds} seconds...")
                time.sleep(cooldown_seconds)

    print("\n🎉 Processing complete. Results saved to:", output_file)


def process_grouped_invoices(download_folder, output_file, log_file="completed_invoices.txt", prompt_text=None):
    """
    Groups attachments by invoice ID and runs OCR extraction on each group.
    """
    prompt_text = prompt_text or (
        "Give me the date of charges and the charge amount from these invoices in a table format. "
        "REMEMBER: If the pdf does not contain a dollar amount but dates are present - then only include the dates"
    )

    all_files = glob.glob(os.path.join(download_folder, "**"), recursive=True)
    valid_exts = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
    valid_files = [
    f for f in all_files
    if os.path.isfile(f) and os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ]

    invoice_map = defaultdict(list)
    for path in valid_files:
        invoice_id = extract_invoice_id(os.path.basename(path))
        if invoice_id:
            invoice_map[invoice_id].append(path)

    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            completed_invoices = set(line.strip() for line in f if line.strip())
    else:
        completed_invoices = set()

    print(f"📁 Found {len(invoice_map)} unique invoices with valid attachments")
    print(f"🧾 {len(completed_invoices)} invoice(s) already processed. Skipping those.")

    with open(output_file, "a", encoding="utf-8") as out_file, \
         open(log_file, "a", encoding="utf-8") as log:
        for idx, (invoice_id, files) in enumerate(invoice_map.items(), start=1):
            if invoice_id in completed_invoices:
                print(f"[{idx}] ⏭️ Skipping already processed invoice: {invoice_id}")
                continue

            print(f"\n[{idx}] 🔄 Processing invoice: {invoice_id} with {len(files)} attachments")
            combined_response = ""

            try:
                for path in files:
                    file_name = os.path.basename(path)
                    print(f"  📤 Uploading {file_name}...")
                    url = upload_pdf(path)
                    response = ask_pdf_questions(prompt_text, url)
                    combined_response += f"File: {file_name}\n{response}\n\n"

                out_file.write(f"Invoice: {invoice_id}\n{combined_response}{'='*80}\n")
                log.write(f"{invoice_id}\n")
                log.flush()

                print(f"✅ Done: Invoice {invoice_id}")
            except Exception as e:
                print(f"❌ Error processing invoice {invoice_id}: {e}")

    print("\n🎉 All invoices processed. Results saved to:", output_file)
