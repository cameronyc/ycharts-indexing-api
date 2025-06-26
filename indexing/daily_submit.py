import csv
import os
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# === CONFIG =========================================================
API_CREDENTIALS = "indexing/ycharts-indexing-api.json"

# • Default to the new rotating list …
# • …but let prod override it with:  export URLS_CSV_PATH=indexing/urls.csv
URLS_CSV = os.getenv("URLS_CSV_PATH", "indexing/urls_rotating.csv")

LOG_CSV = "indexing/log.csv"           # keeps a running success/error log
MAX_SUBMISSIONS = 200                  # daily API quota safety-valve
SLEEP_SECONDS = 1                      # polite delay between calls
# ====================================================================

# === AUTH ===
SCOPES = ["https://www.googleapis.com/auth/indexing"]
credentials = service_account.Credentials.from_service_account_file(
    API_CREDENTIALS, scopes=SCOPES
)
service = build("indexing", "v3", credentials=credentials, cache_discovery=False)

# === LOAD URLS ===
def read_urls(path):
    try:
        with open(path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ URLs file not found: {path}")
        return []

# === LOG RESULTS ===
def log_submission(url, status):
    os.makedirs(os.path.dirname(LOG_CSV), exist_ok=True)
    with open(LOG_CSV, "a", newline="") as log:
        csv.writer(log).writerow([datetime.now().isoformat(), url, status])

# === SUBMIT ONE URL ===
def submit_url(url):
    body = {"url": url, "type": "URL_UPDATED"}
    try:
        service.urlNotifications().publish(body=body).execute()
        log_submission(url, "SUCCESS")
        print(f"✅ Indexed: {url}")
    except Exception as e:
        log_submission(url, f"ERROR: {e}")
        print(f"❌ Failed:  {url} — {e}")

# === MAIN ===
def main():
    urls = read_urls(URLS_CSV)[:MAX_SUBMISSIONS]
    if not urls:
        print("No URLs to submit — exiting.")
        return

    print(f"📦 Submitting {len(urls)} URLs from {URLS_CSV} …")
    for url in urls:
        submit_url(url)
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
