from bs4 import BeautifulSoup
import requests


# Standar headers to mimic a real browser request
HEADERS = {
    # Windows
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

    #Linux
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}

# Cache URL 
URL = None

# Store page content globally to avoid repeated fetches
SOUP = None

# Cache page title globally
PAGE_TITLE = None



def __fetch_website_contents(url):
    """
    Load the content of the website at the given url.
    """

    # Declare globals to update them
    global URL, SOUP, PAGE_TITLE


    # Retrieve the webpage content
    response = requests.get(url, headers=HEADERS)

    # Raise an error for bad responses
    response.raise_for_status()

    # Parse the HTML content using BeautifulSoup
    SOUP = BeautifulSoup(response.content, "html.parser")

    # Update new url
    URL = url

    # Cache the page title
    PAGE_TITLE = SOUP.title.string if SOUP.title else "No Title Found"

    

def fetch_text_contents(url):
    """
    Return the title and contents of the website at the given url,
    truncate to 2,000 characters as a sensible limit
    """

    if SOUP is None or URL != url:
        __fetch_website_contents(url)
    
    # Read all text content from the webpage
    if SOUP and SOUP.body:
        # Remove unwanted contents
        for irrelevant in SOUP(['script', 'style', 'img', 'input']):
            irrelevant.decompose();
        content = SOUP.body.get_text(separator='\n', strip=True)
    else:
        content = "No Body Content Found"

    return (PAGE_TITLE + "\n\n" + content)[:2000]



def fetch_website_links(url):
    """
    Return all the links found on the webpage.
    """

    if SOUP is None or URL != url:
        __fetch_website_contents(url)

    if SOUP and SOUP.body:
        links = []
        for a_tag in SOUP.find_all('a', href=True):
            links.append(a_tag['href'])
        
        return links
    else:
        return []


