import csv
import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Constants
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
KEY_FILE = "indexing/ycharts-search-console-api.json"
SITE_URL = "sc-domain:ycharts.com"  # Verified property
URLS_FILE = "indexing/urls.csv"
LOG_FILE = "indexing/impact_log.csv"

# Authenticate and build the Search Console API service
def authenticate():
    credentials = service_account.Credentials.from_service_account_file(
        KEY_FILE, scopes=SCOPES
    )
    service = build("searchconsole", "v1", credentials=credentials)
    return service

# Query performance data for a single URL
def fetch_data(service, url, start_date, end_date):
    request = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page"],
        "dimensionFilterGroups": [
            {
                "filters": [
                    {
                        "dimension": "page",
                        "operator": "equals",
                        "expression": url,
                    }
                ]
            }
        ],
        "rowLimit": 1,
    }

    response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()
    rows = response.get("rows", [])
    if rows:
        clicks = rows[0]["clicks"]
        impressions = rows[0]["impressions"]
        position = rows[0]["position"]
        return clicks, impressions, position
    else:
        return 0, 0, 0

def main():
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)

    service = authenticate()

    # Read URLs from urls.csv
    with open(URLS_FILE, newline="") as f:
        reader = csv.reader(f)
        urls = [row[0].strip() for row in reader if row]

    # Write performance data to log
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        for url in urls:
            clicks, impressions, position = fetch_data(service, url, str(seven_days_ago), str(today))
            writer.writerow([datetime.date.today(), url, clicks, impressions, position])
            print(f"✅ {url} — Clicks: {clicks}, Impressions: {impressions}, Position: {position}")

if __name__ == "__main__":
    main()
