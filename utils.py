import json
import re
import requests
from bs4 import BeautifulSoup
import time


# Cleaning Functions
def clean_text(text):
    """Clean text by removing HTML tags, URLs, and non-alphabet characters, and normalize spaces."""
    text = re.sub(r'<[^>]+>', '', text)  #  HTML tags
    text = re.sub(r'http\S+', '', text)  #  URLs
    text = re.sub(r'[^a-zA-Z\s]', '', text)  #  non-alphabet characters
    text = text.lower().strip()  # conversion to lowercase and strip whitespace
    return re.sub(r'\s+', ' ', text)  # now let's replace  multiple spaces with single space


def clean_data(file_path, output_path):
    """Load data from a file, clean its content, and save the cleaned data back to another file."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    cleaned_data = [{'url': item['url'], 'content': clean_text(item['content'])} for item in data]
    with open(output_path, 'w') as file:
        json.dump(cleaned_data, file, indent=4)


# Scraping Functions
def scrape_site(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = ' '.join(p.get_text() for p in soup.find_all('p'))

        # find subpage links within the main page so not only the main page is scraped
        subpage_links = set(a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith(url))
        subpage_texts = [main_content]

        for link in subpage_links:
            sub_response = requests.get(link)
            sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
            subpage_text = ' '.join(p.get_text() for p in sub_soup.find_all('p'))
            subpage_texts.append(subpage_text)

        all_text = ' '.join(subpage_texts)
        cleaned_text = clean_text(all_text)
        # cut to first 8000 characters to ensure it fits within token limits
        return cleaned_text[:8000]
    except requests.RequestException as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

# Embedding Functions
import openai


def generate_embeddings(content):
    # Tokenize the content and check if it exceeds the maximum limit
    max_length = 8192  # Max tokens the model can handle
    tokens = content.split()
    if len(tokens) > max_length:
        content = ' '.join(tokens[:max_length])  # cut to the max length

    try:
        response = openai.Embedding.create(input=content, model="text-embedding-ada-002")
        if 'data' in response and 'embedding' in response['data'][0]:
            return response['data'][0]['embedding']
        else:
            print("No embedding found in response")
            return None
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None


# Data Saving and Loading Functions
def already_exists(url, embeddings_data):
    """Check if the URL is already in the embeddings data."""
    return any(entry['url'] == url for entry in embeddings_data)

def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def load_data(filename):
    """Load data from a JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)
