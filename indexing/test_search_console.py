import datetime
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define the scope for Search Console API
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

# Path to your Search Console credential file
SERVICE_ACCOUNT_FILE = 'indexing/ycharts-search-console-api.json'

# Use the verified domain property in GSC (no www.)
site_url = 'sc-domain:ycharts.com'

# Date range for query (7-day rolling window)
end_date = datetime.date.today().isoformat()
start_date = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()

# Authenticate and create the Search Console API client
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('searchconsole', 'v1', credentials=credentials)

# Read URLs from input CSV and normalize them
with open('indexing/top_200_companies.csv', newline='') as csvfile:
    url_reader = csv.reader(csvfile)
    urls = [
        row[0].strip().replace("www.ycharts.com", "ycharts.com")
        for row in url_reader
        if row and row[0].strip().startswith("http")
    ]

# Write results to log
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
            if 'rows' in response:
                row = response['rows'][0]
                clicks = row.get('clicks', 0)
                impressions = row.get('impressions', 0)
                position = row.get('position', 0)
                status = 'Success'
            else:
                clicks = impressions = position = 0
                status = 'No Data'

            print(f"✅ {url} — Clicks: {clicks}, Impressions: {impressions}, Position: {position}")
            log_writer.writerow([datetime.date.today(), url, clicks, impressions, position, status])

        except Exception as e:
            print(f"❌ Error fetching data for {url}: {e}")
            log_writer.writerow([datetime.date.today(), url, 'ERROR', 'ERROR', 'ERROR', 'Error'])
