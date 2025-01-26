import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.asyncio import tqdm

# Base URL for topics
base_url = "https://www.goodreads.com/shelf/show/"

# User-Agent to avoid 403 error
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to fetch a single page asynchronously
async def fetch_page(session, url):
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Failed to fetch {url}: {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to process a single topic asynchronously
async def process_topic(session, topic):
    url = base_url + topic
    html_content = await fetch_page(session, url)
    data = []
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        for book in soup.find_all('a', class_='bookTitle'):
            book_title = book.text.strip()
            book_url = book['href']
            data.append([topic, book_title, book_url])
    return data

# Main async function
async def main():
    # Read all the topics from the csv, column name is 'Topic'
    topics = pd.read_csv('goodreads_topics.csv')['Topic']

    # List to store extracted data
    all_data = []

    async with aiohttp.ClientSession() as session:
        # Use asyncio.gather to process all topics concurrently
        tasks = [process_topic(session, topic) for topic in topics]
        results = await tqdm.gather(*tasks, desc="Processing topics")

        # Combine all results
        for result in results:
            if result:
                all_data.extend(result)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(all_data, columns=['Topic', 'Book Title', 'Book URL'])

    # Order the DataFrame by Book Title
    df.sort_values(by='Topic', inplace=True)

    # Delete rows with duplicate URLs
    df.drop_duplicates(subset='Book URL', inplace=True)

    # Save the DataFrame to a CSV file
    df.to_csv('goodreads_shelves.csv', index=False)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
