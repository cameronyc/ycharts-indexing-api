import csv
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load Indexing API credentials
credentials = service_account.Credentials.from_service_account_file(
    'indexing/ycharts-indexing-api.json',
    scopes=["https://www.googleapis.com/auth/indexing"]
)

# Build the Indexing API service
service = build('indexing', 'v3', credentials=credentials)

# Paths
url_csv_path = "indexing/top_200_companies.csv"
log_csv_path = "indexing/log.csv"

# Load URLs from CSV
with open(url_csv_path, "r") as file:
    reader = csv.reader(file)
    urls = [row[0] for row in reader if row and row[0].strip() != ""]

# Submit URLs
log_rows = []
today = datetime.utcnow().strftime('%Y-%m-%d')

for count, url in enumerate(urls[:200]):  # cap to 200/day
    body = {
        "url": url,
        "type": "URL_UPDATED"
    }
    try:
        response = service.urlNotifications().publish(body=body).execute()
        print(f"✅ [{count+1}] Submitted: {url}")
        log_rows.append([today, url, "Success"])
    except Exception as e:
        print(f"❌ [{count+1}] Failed: {url} — {str(e)}")
        log_rows.append([today, url, "Failed", str(e)])

# Write log
with open(log_csv_path, "a", newline='') as logfile:
    writer = csv.writer(logfile)
    for row in log_rows:
        writer.writerow(row)

print("\n📘 Submission complete. Logged to log.csv.")
