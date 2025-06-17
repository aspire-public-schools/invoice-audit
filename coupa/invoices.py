import os
import pickle
from .auth import get_access_token
from .utils import log
import requests

def get_invoice_details(invoice_id, access_token=None):
    if access_token is None:
        access_token = get_access_token()
        if not access_token:
            raise ValueError("Unable to obtain a valid access token.")

    base_url = os.getenv("URL")
    endpoint = f"{base_url}/api/invoices/{invoice_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code != 200:
        log(f"Failed to retrieve invoice details for invoice {invoice_id}. Status code: {response.status_code}", "error")
        log(response.text, "error")
    else:
        log(response.text)
        log(f"Successfully retrieved invoice details for invoice {invoice_id}.", "success")

    return response


#USE THIS FUNCTION ONLY IF YOU NEED TO READ DATA FROM THE PYTHON OBJECT AFTER THE PROGRAM HAS EXECUTED - THIS ALLOWS RETAINING DATA ON DISK    

def save_invoice_details_as_pickle(invoice_ids, output_pickle="invoice_details.pkl"):
    access_token = get_access_token()
    if not access_token:
        raise ValueError("Failed to get access token.")

    invoice_data = []

    for idx, invoice_id in enumerate(invoice_ids, start=1):
        log(f"[{idx}/{len(invoice_ids)}] Fetching invoice: {invoice_id}", "info")
        response = get_invoice_details(invoice_id, access_token)

        if response.status_code == 200:
            try:
                data = response.json()
                invoice_data.append(data)
            except Exception as e:
                log(f"Failed to parse JSON for invoice {invoice_id}: {e}", "warn")
        else:
            log(f"Skipped invoice {invoice_id} due to API error.", "warn")

    with open(output_pickle, "wb") as f:
        pickle.dump(invoice_data, f)

    log(f"Saved {len(invoice_data)} invoice(s) to: {output_pickle}", "success")