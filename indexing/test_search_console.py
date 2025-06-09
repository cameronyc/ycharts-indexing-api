import datetime
import csv
from urllib.parse import urlparse
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define the scope for Search Console API
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

# Path to your Search Console credential file
SERVICE_ACCOUNT_FILE = 'indexing/ycharts-search-console-api.json'

# GSC site property (must match your actual GSC setup — using domain property here)
site_url = 'sc-domain:ycharts.com'

# Date range (last 7 days)
end_date = datetime.date.today().isoformat()
start_date = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()

# Authenticate and create service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('searchconsole', 'v1', credentials=credentials)

# Read URLs from the input file (ensure proper formatting)
with open('indexing/top_200_companies.csv', newline='') as csvfile:
    url_reader = csv.reader(csvfile)
    urls = [row[0].strip() for row in url_reader if row and row[0].strip().startswith("http")]

# Prepare to write results
with open('indexing/impact_log.csv', mode='w', newline='') as logfile:
    log_writer = csv.writer(logfile)
    log_writer.writerow(['Date', 'URL', 'Clicks', 'Impressions', 'Avg Position', 'Status'])

    for url in urls:
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['page'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': url
                }]
            }]
        }

        try:
            response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            if 'rows' in response and len(response['rows']) > 0:
                row = response['rows'][0]
                clicks = row.get('clicks', 0)
                impressions = row.get('impressions', 0)
                position = round(row.get('position', 0), 2)
                log_writer.writerow([datetime.date.today(), url, clicks, impressions, position, "Success"])
                print(f"✅ {url} — Clicks: {clicks}, Impressions: {impressions}, Position: {position}")
            else:
                log_writer.writerow([datetime.date.today(), url, 0, 0, 0, "No data"])
                print(f"⚠️  {url} — No data found.")

        except Exception as e:
            log_writer.writerow([datetime.date.today(), url, "ERROR", "ERROR", "ERROR", f"Error: {str(e)}"])
            print(f"❌ {url} — Error: {e}")
