import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

#  User-Agent header to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

#  CSV file name
csv_file = 'soberhouse_listings1.csv'

#  Initialize CSV with headers (only if not exists)
try:
    df = pd.read_csv(csv_file)
    print(f" Existing file found: {csv_file}")
except FileNotFoundError:
    df = pd.DataFrame(columns=['Name', 'PhoneNumber', 'Address', 'Website'])
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f" New CSV created: {csv_file}")

#  Function with retry logic
def get_soup(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                print(f"⚠️ Failed with status {response.status_code} for {url}")
        except Exception as e:
            print(f" Error fetching {url}: {e}")
        print(f"🔄 Retrying ({attempt + 1}/{retries})...")
        time.sleep(random.uniform(2, 5))  # wait before retry
    print(f" Skipping {url} after {retries} failed attempts")
    return None


# ✅ Step 1: Get all state links
base_url = "https://soberhouse.com/find/"
soup = get_soup(base_url)
if not soup:
    print(" Could not load the base URL.")
    exit()

state_links = [
    a['href'] for a in soup.select('div.listings.clearfix ul.states li a')
]
print(f"🌍 Found {len(state_links)} states")

#  Step 2: Loop over states
for state_link in state_links:
    soup = get_soup(state_link)
    if soup is None:
        continue

    city_links = [
        a['href'] for a in soup.select('div.listings.clearfix ul.cities li a')
    ]
    print(f"\n🌎 State URL: {state_link} - {len(city_links)} cities")

    #  Step 3: Loop over cities
    for city_link in city_links:
        print(f"City: {city_link}")
        soup = get_soup(city_link)
        if soup is None:
            continue

        card_links = list(set(
            [a['href'] for a in soup.select('div#centers_listing > div > a')]
        ))
        print(f" Found {len(card_links)} unique listings")

        #  Step 4: Loop over listings
        for link in card_links:
            soup = get_soup(link)
            if soup is None:
                continue

            try:
                name = soup.select_one('#contents article h1').get_text(strip=True)
            except:
                name = ''

            try:
                address = soup.select_one('#center_profile div span:nth-of-type(1) p').get_text(strip=True)
            except:
                address = ''

            try:
                phone = soup.select_one('#center_profile div span:nth-of-type(2) p').get_text(strip=True)
            except:
                phone = ''

            try:
                website = soup.select_one('#center_profile div p a')['href'].strip()
            except:
                website = ''

            row = {
                'Name': name,
                'PhoneNumber': phone,
                'Address': address,
                'Website': website
            }

            #  Append the row to CSV immediately
            pd.DataFrame([row]).to_csv(csv_file, mode='a', index=False, header=False, encoding='utf-8')

            print(f"      ✔️ {name} extracted and saved")

            time.sleep(random.uniform(1.5, 4))  # polite delay

print("\n All data saved to", csv_file)
