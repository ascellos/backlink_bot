import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")

def post_to_devto(title: str, body_markdown: str, tags=None):
    """
    Publishes an article to dev.to using their official API.
    Returns the response JSON, which includes the live article URL.
    """
    url = "https://dev.to/api/articles"
    headers = {
        "api-key": DEVTO_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": True,
            "tags": tags or []
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # raises an error if the request failed
    return response.json()