#!/usr/bin/env python3
"""
FHIR Medication Downloader

This script downloads medication resources from a FHIR server
and saves them as JSON files in the data directory.
"""

import requests
import json
import math
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

API_AUTH_HEADER = os.getenv("API_AUTH_HEADER", "Ocp-Apim-Subscription-Key")
API_KEY = os.getenv("API_KEY", "")
API_ENDPOINT = os.getenv("API_ENDPOINT", "https://at-api.legemiddelverket.no/fhir-r4")
DATA_DIR = Path(__file__).parent / "data"
PAGE_SIZE = 100
PAUSE_MS = 1000

# FHIR resource type to local directory name mapping
RESOURCES = {
    "SubstanceSpecification": "substance-specification",
    "MedicinalProductIngredient": "med-prod-ingr",
    "MedicinalProductManufactured": "med-prod-man",
    "MedicinalProductPharmaceutical": "med-prod-pharm",
    "MedicinalProductPackaged": "med-prod-pkg",
    "MedicinalProduct": "med-prod",
    "Basic": "basic",
    "ValueSet": "value-set",
    "CodeSystem": "code-system",
}


def log(msg):
    print(msg, flush=True)


def download_resource_type(session, resource_type, dirname):
    target = Path(DATA_DIR) / dirname
    target.mkdir(parents=True, exist_ok=True)

    url = f"{API_ENDPOINT.rstrip('/')}/{resource_type}"

    count_response = session.get(url, params={"_summary": "count"}, timeout=60)
    count_response.raise_for_status()
    total = count_response.json().get("total")
    total_pages = math.ceil(total / PAGE_SIZE) if total is not None else None
    log(f"[{resource_type}] Total resources on server: {total}")
    time.sleep(PAUSE_MS / 1000)

    params = {"_count": PAGE_SIZE}
    page = 0
    saved = 0

    while url:
        page += 1
        log(f"[{resource_type}] Fetching page {page}/{total_pages or '?'}: {url}")
        response = session.get(url, params=params, timeout=60)
        response.raise_for_status()
        bundle = response.json()
        params = None  # the "next" link already carries its query string

        for entry in bundle.get("entry", []):
            resource = entry.get("resource")
            if not resource or "id" not in resource:
                continue
            path = target / f"{resource['id']}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(resource, f, ensure_ascii=False, indent=2)
            saved += 1
        log(f"[{resource_type}] Page {page}/{total_pages or '?'} done, {saved}/{total if total is not None else '?'} resources saved")

        url = next(
            (l.get("url") for l in bundle.get("link", []) if l.get("relation") == "next"),
            None,
        )
        if url:
            time.sleep(PAUSE_MS / 1000)

    log(f"[{resource_type}] Finished: {saved}/{total if total is not None else '?'} resources in {target}")


def main():
    if not API_KEY:
        log("ERROR: API_KEY environment variable is not set. Aborting.")
        sys.exit(1)

    session = requests.Session()
    session.headers.update({"Accept": "application/fhir+json"})
    session.headers[API_AUTH_HEADER] = API_KEY

    for resource_type, dirname in RESOURCES.items():
        download_resource_type(session, resource_type, dirname)


if __name__ == "__main__":
    main()
