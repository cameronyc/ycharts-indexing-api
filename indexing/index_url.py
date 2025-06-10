import csv
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials
credentials = service_account.Credentials.from_service_account_file(
    'indexing/ycharts-indexing-api.json',
    scopes=["https://www.googleapis.com/auth/indexing"]
)

# Build the service
service = build('indexing', 'v3', credentials=credentials)

# Load URLs from urls.csv
with open('indexing/urls.csv', newline='') as csvfile:
    url_reader = csv.reader(csvfile)
    urls = [row[0].strip() for row in url_reader if row and row[0].strip().startswith("http")]

# Log results to log.csv
with open('indexing/indexing_log.csv', mode='a', newline='') as logfile:
    log_writer = csv.writer(logfile)
    log_writer.writerow(['Date', 'URL', 'Status', 'Message'])

    for url in urls:
        body = {
            "url": url,
            "type": "URL_UPDATED"
        }

        try:
            response = service.urlNotifications().publish(body=body).execute()
            print("✅ Submitted:", url)
            log_writer.writerow([datetime.date.today(), url, "Success", "Submitted"])
        except Exception as e:
            print("❌ Failed:", url, "Error:", e)
            log_writer.writerow([datetime.date.today(), url, "Fail", str(e)])
