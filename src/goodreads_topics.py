import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL for topics
base_url = "https://www.goodreads.com/topics/list?page="
suffix = ''

# List to store extracted data
data = []

# User-Agent to avoid 403 error
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Loop through all 14 pages
for page in range(1, 15):
    url = f"{base_url}{page}{suffix}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        topics = soup.find_all('div', class_='shelfStat')

        for topic in topics:
            topic_name = topic.find('a', class_='mediumText actionLinkLite').text.strip()
            book_count = topic.find('div', class_='smallText greyText').text.strip()
            # remove the subfix " books", the comma and convert to integer
            book_count = int(book_count.replace(" books", "").replace(",", ""))
            data.append((topic_name, book_count))
    else:
        print(f"Failed to fetch page {page} ({url}), got code {response.status_code}")

# Create a DataFrame
columns = ['Topic', 'Book Count']
df = pd.DataFrame(data, columns=columns)

# Order by book count
df = df.sort_values(by='Topic')

# Save to CSV
df.to_csv('goodreads_topics.csv', index=False)

print("Data has been extracted and saved to 'goodreads_topics.csv'")
