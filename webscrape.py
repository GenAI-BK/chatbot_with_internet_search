from urllib.parse import urlparse
from html2text import HTML2Text  # Library for converting HTML to plain text
import requests  # Library for making HTTP requests
from requests.auth import HTTPBasicAuth  # Library for HTTP basic authentication
from bs4 import BeautifulSoup


#------------------------- Settings Start-------------------------------------
# Define settings for the script
RETRIES = 5
DELAY = 1
USERNAME = 'your_username'  # Your username for basic authentication 
PASSWORD = 'your_password'  # Your password for basic authentication 
USE_AUTHENTICATION = True  # Whether to use authentication or not
#------------------------- Settings End---------------------------------------


def fetch_with_retry_auth(url, retries=RETRIES, delay=DELAY):
    """
    Fetches the content of a URL with retries and optional authentication.

    Parameters:
    url (str): The URL to fetch.
    retries (int): Number of retries in case of failure.
    delay (int): Delay (in seconds) between retries.

    Returns:
    str: HTML content of the page if successful, None otherwise.
    """
    for _ in range(retries):
        try:
            if USE_AUTHENTICATION:
                response = requests.get(url, timeout=20, auth=HTTPBasicAuth(USERNAME, PASSWORD))
            else:
                response = requests.get(url, timeout=20)

            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to fetch {url}. Status code: {response.status_code}")

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

        time.sleep(delay)

    return None  # Return None if all retries fail

def fetch_and_save(url, content_filename):
    """
    Fetches the content of a URL, extracts clean text, and saves it to a file.

    Parameters:
    url (str): The URL to fetch.
    content_filename (str): File name to save the content.

    Returns:
    None
    """
    html_content = fetch_with_retry_auth(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove unwanted sections
        for element in soup(["header", "footer", "nav", "script", "style"]):
            element.decompose()

        # Convert HTML to plain text
        html2text_transformer = HTML2Text()
        html2text_transformer.ignore_links = True
        html2text_transformer.ignore_images = True
        plain_text_content = html2text_transformer.handle(str(soup))

        # Save content to file
        with open(content_filename, "w", encoding="utf-8") as file:
            file.write(f"Source URL: {url}\n\n")
            file.write(plain_text_content)
            file.write(f"\n\nSource URL: {url}\n")

        print(f"Data from {url} saved to {content_filename}")
    else:
        print("Failed to retrieve content.")

# Example usage
# url = "https://www.geeksforgeeks.org/introduction-to-directed-acyclic-graph/"
# fetch_and_save(url, "output.txt")

# def fetch_with_retry_auth(url, retries=RETRIES, delay=DELAY):
#     """
#     Fetches the content of a URL with retries in case of failure, including basic authentication.
    
#     Parameters:
#     url (str): The URL to fetch.
#     retries (int): Number of retries in case of failure.
#     delay (int): Delay between retries.
    
#     Returns:
#     requests.Response or None: The response object if successful, None otherwise.
#     """
#     if USE_AUTHENTICATION:
#         for _ in range(retries):
#             try:
#                 response = requests.get(url, timeout=20, auth=HTTPBasicAuth(USERNAME, PASSWORD))
#                 if response.status_code == 200:
#                     return response
#             except Exception as e:
#                 print(f"Error fetching {url}: {e}")
#             time.sleep(delay)
#     else:
#         for _ in range(retries):
#             try:
#                 response = requests.get(url, timeout=20)
#                 if response.status_code == 200:
#                     return response
#             except Exception as e:
#                 print(f"Error fetching {url}: {e}")
#             time.sleep(delay)
#     return None


# def fetch_and_save(url_1, content_filename,URL):
#     """
#     Fetches the content of a URL, cleans it, and saves it as a text file.
    
#     Parameters:
#     url_1 (str): The URL to fetch.
#     content_filename (str): The name of the file to save the content.
#     existing_urls (set): Set of existing URLs to avoid duplicates.
#     """
#     response = fetch_with_retry_auth(url_1)
#     if response:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         for element in soup(["header", "footer", "nav"]):
#             element.decompose()

#         html2text_transformer = HTML2Text()
#         html2text_transformer.ignore_links = False
#         html2text_transformer.ignore_images = True
#         plain_text_content = html2text_transformer.handle(str(soup))
#         with open(content_filename, "w", encoding="utf-8") as file:
#             file.write(url_1 + "\n")
#             file.write(plain_text_content)
#             file.write(url_1 + "\n")
#             print(f"Data from {url_1} saved to {content_filename}")