import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.asyncio import tqdm

# Base URL for Goodreads
base_url = "https://www.goodreads.com"

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
                with open("fetch_errors.log", "a") as log_file:
                    log_file.write(f"Failed to fetch {url}: {response.status}\n")
                return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        with open("fetch_errors.log", "a") as log_file:
            log_file.write(f"Error fetching {url}: {e}\n")
        return None

# Function to extract book details from a Goodreads book page
async def extract_book_details(session, topic, book_url):
    url = base_url + book_url
    html_content = await fetch_page(session, url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        title = soup.find('h1', {'class': 'Text__title1', 'data-testid': 'bookTitle'}).text.strip()
    except AttributeError:
        title = None

    try:
        author = soup.find('a', {'class': 'ContributorLink'})
        author_name = author.find('span', {'data-testid': 'name'}).text.strip()
        author_url = author['href']
    except AttributeError:
        author_name = None
        author_url = None

    book_details = {
        'Pages': None,
        'Format': None,
        'Publication Info': None
    }

    try:
        edition_section = soup.find('div', {'class': 'FeaturedDetails'})
        if edition_section:
            for p in edition_section.find_all('p'):
                if 'data-testid' in p.attrs:
                    key = p['data-testid']
                    value = p.text.strip()
                    if key == 'pagesFormat':
                        pages_format = value.split(',')
                        if len(pages_format) == 2:
                            book_details['Pages'] = pages_format[0].strip().replace(" pages", "")
                            book_details['Format'] = pages_format[1].strip()
                    elif key == 'publicationInfo':
                        # Data is "First published July 25, 2023" convert it into a date
                        value = value.replace("First published ", "")
                        # Now convert "July 25, 2023" into a date
                        date_parts = value.split(' ')
                        if len(date_parts) == 3:
                            month = date_parts[0]
                            # Convert month from text to number
                            months = {
                                "January": "01",
                                "February": "02",
                                "March": "03",
                                "April": "04",
                                "May": "05",
                                "June": "06",
                                "July": "07",
                                "August": "08",
                                "September": "09",
                                "October": "10",
                                "November": "11",
                                "December": "12"
                            }
                            month = months[month]
                            day = date_parts[1].replace(",", "")
                            year = date_parts[2]
                            book_details['Publication Info'] = f"{year}-{month}-{day}"
    except AttributeError as e:
        print(f"Error processing FeaturedDetails: {e}")

    try:
        genres = [
            a['href'] for a in soup.select('span.BookPageMetadataSection__genreButton a.Button--tag')
        ]
        genres = [genre.replace("https://www.goodreads.com/genres/", "") for genre in genres]
    except AttributeError:
        genres = []

    return {
        'Topic': topic,
        'Title': title,
        'Author Name': author_name,
        'Author URL': author_url,
        'Pages': book_details['Pages'],
        'Format': book_details['Format'],
        'Publication Info': book_details['Publication Info'],
        'Genres': genres,
        'Book URL': url
    }

# Main async function
async def main():
    books_df = pd.read_csv('goodreads_shelves.csv')
    max_rows = 10
    books_df = books_df.head(max_rows)
    all_data = []

    async with aiohttp.ClientSession() as session:
        tasks = [
            extract_book_details(session, row['Topic'], row['Book URL'])
            for _, row in books_df.iterrows()
        ]
        
        results = await tqdm.gather(*tasks, desc="Processing books")
        all_data = [res for res in results if res]

    df = pd.DataFrame(all_data)
    df.to_csv('goodreads_book_details.csv', index=False)

if __name__ == "__main__":
    asyncio.run(main())
