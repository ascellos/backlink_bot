import requests

def verify_backlink(published_url: str, client_site: str):
    """
    Visits the published URL and checks if it still contains a link to client_site.
    Returns 'live' if found, 'broken' if not found or unreachable.
    """
    try:
        response = requests.get(published_url, timeout=10)
        if response.status_code != 200:
            return "broken"
        
        # Check if the client site URL appears anywhere in the page's HTML
        if client_site in response.text:
            return "live"
        else:
            return "removed"  # page loads, but the link is gone
            
    except requests.exceptions.RequestException:
        return "broken"  # page didn't load at all