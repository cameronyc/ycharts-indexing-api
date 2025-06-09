import csv
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# === CONFIG ===
API_CREDENTIALS = "indexing/ycharts-indexing-api.json"
URLS_CSV = "indexing/urls.csv"
LOG_CSV = "indexing/log.csv"
MAX_SUBMISSIONS = 200

# === AUTH ===
SCOPES = ["https://www.googleapis.com/auth/indexing"]
credentials = service_account.Credentials.from_service_account_file(API_CREDENTIALS, scopes=SCOPES)
service = build("indexing", "v3", credentials=credentials)

# === LOAD URLS ===
def read_urls(filepath):
    with open(filepath, "r") as file:
        return [line.strip() for line in file if line.strip()]

# === LOG RESULTS ===
def log_submission(url, status):
    with open(LOG_CSV, "a", newline="") as log:
        writer = csv.writer(log)
        writer.writerow([datetime.now().isoformat(), url, status])

# === SUBMIT ===
def submit_url(url):
    try:
        body = {"url": url, "type": "URL_UPDATED"}
        response = service.urlNotifications().publish(body=body).execute()
        log_submission(url, "SUCCESS")
        print(f"✅ Indexed: {url}")
    except Exception as e:
        log_submission(url, f"ERROR: {e}")
        print(f"❌ Failed: {url} — {e}")

# === MAIN ===
def main():
    urls = read_urls(URLS_CSV)[:MAX_SUBMISSIONS]
    print(f"📦 Submitting up to {len(urls)} URLs...")

    for i, url in enumerate(urls, 1):
        submit_url(url)
        time.sleep(1)  # Be nice to the API

if __name__ == "__main__":
    main()
