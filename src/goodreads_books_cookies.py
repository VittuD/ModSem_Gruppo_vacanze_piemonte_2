import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.asyncio import tqdm
import json
import os

# Base URL for Goodreads
base_url = "https://www.goodreads.com"

# Change dir to '/workspaces/ModSem_Gruppo_vacanze_piemonte_2/src'
os.chdir("/workspaces/ModSem_Gruppo_vacanze_piemonte_2/src")

# Load cookies from a file
def load_cookies():
    with open("cookies.json", "r") as f:
        cookies = json.load(f)
    return {cookie['name']: cookie['value'] for cookie in  cookies}

# Function to fetch a single page asynchronously with a delay
async def fetch_page(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                with open("full_text_debug.html", "w") as debug_file:
                    debug_file.write(html_content)
                return html_content
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

    # Find script id="__NEXT_DATA__" and extract JSON data
    try:
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        script_json = json.loads(script.string)

        with open("apolloState_debug.json", "w") as debug_file:
            json.dump(script_json['props']['pageProps']['apolloState'], debug_file, indent=4)
            
        # Extract keys from apolloState    
        apolloStateKeys = list(script_json['props']['pageProps']['apolloState'].keys())
        # The book_key starts 'Book:' prefix
        book_key = [key for key in apolloStateKeys if key.startswith('Book:')][0]
        work_key = [key for key in apolloStateKeys if key.startswith('Work:')][0]
        series_keys = [key for key in apolloStateKeys if key.startswith('Series:')]
        contributor_keys = [key for key in apolloStateKeys if key.startswith('Contributor:')]
        # For each contributor key, remove it if not present in script_json['props']['pageProps']['apolloState'][book_key] (serch as text)
        book_key_strin = script_json['props']['pageProps']['apolloState'][book_key].__str__()
        contributor_keys = [key for key in contributor_keys if key in book_key_strin]

        relevant_keys = [book_key, work_key] + series_keys + contributor_keys

        # Extract book details (every key )
        book_details = {}
        for key in relevant_keys:
            book_details[key] = script_json['props']['pageProps']['apolloState'][key]

        stripped_title = book_details[book_key]['titleComplete'].replace(" ", "_")

        with open(f"book_details/{stripped_title}.json", "w") as debug_file:
            json.dump(book_details, debug_file, indent=4)

    except Exception as e:
        print(f"Error extracting book details from {url}: {e}")
        with open("extract_errors.log", "a") as log_file:
            log_file.write(f"Error extracting book details from {url}: {e}\n")
        return None

# Main async function
async def main():
    cookies = load_cookies()
    cookies_jar = aiohttp.CookieJar()
    for key, value in cookies.items():
        cookies_jar.update_cookies({key: value})

    books_df = pd.read_csv('goodreads_shelves.csv')
    max_rows = 20
    books_df = books_df.head(max_rows)
    all_data = []

    async with aiohttp.ClientSession(cookie_jar=cookies_jar) as session:
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
