import pandas as pd
from datetime import datetime
import os

# === CONFIG ===
MASTER_CSV = "indexing/rotating_indexing_urls.csv"
OUTPUT_CSV = "indexing/urls_rotating.csv"

# === Get today's day ===
today = datetime.now().strftime('%A')  # e.g., 'Monday'

# === Read and filter ===
try:
    df = pd.read_csv(MASTER_CSV)

    if 'day' not in df.columns or 'url' not in df.columns:
        raise ValueError("Missing required columns: 'day' and 'url'")

    # Filter for today's rows (case-insensitive match)
    filtered = df[df['day'].str.strip().str.lower() == today.lower()]

    if filtered.empty:
        print(f"⚠️ No URLs found for today ({today}).")
    else:
        filtered['url'].to_csv(OUTPUT_CSV, index=False, header=False)
        print(f"✅ Wrote {len(filtered)} URLs for {today} to {OUTPUT_CSV}")

except FileNotFoundError:
    print(f"❌ Master CSV not found: {MASTER_CSV}")
except Exception as e:
    print(f"❌ Error: {e}")

