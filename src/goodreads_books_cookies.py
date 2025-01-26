import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.asyncio import tqdm
import json
import os

# Change the directory to the desired working directory
os.chdir("/workspaces/ModSem_Gruppo_vacanze_piemonte_2/src")

# Base URL for Goodreads
BASE_URL = "https://www.goodreads.com"

def load_cookies(file_path="cookies.json"):
    """
    Load cookies from a JSON file.

    Args:
        file_path (str): Path to the cookies JSON file.

    Returns:
        dict: A dictionary of cookies to be used for requests.
    """
    try:
        with open(file_path, "r") as f:
            cookies = json.load(f)
        return {cookie['name']: cookie['value'] for cookie in cookies}
    except Exception as e:
        print(f"Error loading cookies: {e}")
        raise

async def fetch_page(session, url):
    """
    Fetch a single page asynchronously.

    Args:
        session (aiohttp.ClientSession): The active aiohttp session.
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the page, or None if an error occurred.
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                log_error(f"Failed to fetch {url}: {response.status}")
                return None
    except Exception as e:
        log_error(f"Error fetching {url}: {e}")
        return None

def log_error(message, file_path="fetch_errors.log"):
    """
    Log an error message to a file.

    Args:
        message (str): The error message to log.
        file_path (str): The path to the log file.
    """
    with open(file_path, "a") as log_file:
        log_file.write(f"{message}\n")

async def extract_book_details(session, topic, book_url):
    """
    Extract book details from a Goodreads book page.

    Args:
        session (aiohttp.ClientSession): The active aiohttp session.
        topic (str): The topic or category of the book.
        book_url (str): The relative URL of the book page.

    Returns:
        dict: A dictionary containing book details, or None if an error occurred.
    """
    url = BASE_URL + book_url
    html_content = await fetch_page(session, url)
    if not html_content:
        return None

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        script_json = json.loads(script.string)

        # Extract keys from apolloState
        apollo_state = script_json['props']['pageProps']['apolloState']
        book_key = next(key for key in apollo_state if key.startswith('Book:'))
        work_key = next(key for key in apollo_state if key.startswith('Work:'))
        series_keys = [key for key in apollo_state if key.startswith('Series:')]
        contributor_keys = [
            key for key in apollo_state if key.startswith('Contributor:')
        ]

        # Filter contributor keys based on their presence in book data
        book_data_str = str(apollo_state[book_key])
        contributor_keys = [key for key in contributor_keys if key in book_data_str]

        # Combine all relevant keys
        relevant_keys = [book_key, work_key] + series_keys + contributor_keys

        # Extract and save book details
        book_details = {key: apollo_state[key] for key in relevant_keys}
        book_details['Topic'] = topic

        stripped_title = book_details[book_key]['titleComplete'].replace(" ", "_")
        save_book_details(book_details, stripped_title)

        return book_details
    except Exception as e:
        log_error(f"Error extracting book details from {url}: {e}", "extract_errors.log")
        return None

def save_book_details(book_details, title, output_dir="book_details"):
    """
    Save book details to a JSON file.

    Args:
        book_details (dict): The book details to save.
        title (str): The sanitized title of the book for the file name.
        output_dir (str): The directory to save the book details.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{title}.json")
    try:
        with open(file_path, "w") as debug_file:
            json.dump(book_details, debug_file, indent=4)
    except Exception as e:
        log_error(f"Error saving book details for {title}: {e}")

async def process_books(session, books_df):
    """
    Process a DataFrame of books and extract their details asynchronously.

    Args:
        session (aiohttp.ClientSession): The active aiohttp session.
        books_df (pd.DataFrame): DataFrame containing book topics and URLs.
    """
    tasks = [
        extract_book_details(session, row['Topic'], row['Book URL'])
        for _, row in books_df.iterrows()
    ]
    await tqdm.gather(*tasks, desc="Processing books")

async def main():
    """
    Main function to orchestrate the fetching and processing of book details.
    """
    cookies = load_cookies()
    cookie_jar = aiohttp.CookieJar()
    for key, value in cookies.items():
        cookie_jar.update_cookies({key: value})

    books_df = pd.read_csv('goodreads_shelves.csv').head(20)

    async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
        await process_books(session, books_df)

if __name__ == "__main__":
    asyncio.run(main())
