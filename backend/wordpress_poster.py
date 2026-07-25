import requests
from requests.auth import HTTPBasicAuth

def post_to_wordpress(site_url: str, username: str, app_password: str, title: str, content_html: str):
    """
    Publishes a post to a WordPress site using the WP REST API.
    Requires an 'Application Password' generated from the WP user's profile.
    """
    endpoint = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    payload = {
        "title": title,
        "content": content_html,
        "status": "publish"
    }
    
    response = requests.post(
        endpoint,
        json=payload,
        auth=HTTPBasicAuth(username, app_password)
    )
    response.raise_for_status()
    return response.json()