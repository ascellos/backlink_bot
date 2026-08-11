import requests
import re
from collections import Counter
from bs4 import BeautifulSoup

STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
              'for', 'of', 'to', 'in', 'on', 'at', 'by', 'with', 'from'}

def get_sitemap_urls(base_url):
    sitemap_url = base_url.rstrip('/') + '/sitemap.xml'
    response = requests.get(sitemap_url, timeout=5)
    if response.status_code != 200:
        return[]

    urls = []
    for line in response.text.split('\n'):
        if '<loc>' in line:
            url = line.split('<loc>')[1].split('</loc>')[0]
            urls.append(url)
    return urls

def pick_pages_to_scrape(urls, base_url, limit=5):
    urls = [u for u in urls if u.startswith(base_url)]
    return urls[:limit]

    
def scrape_page_content(url):
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def get_company_name(soup):
    og_site_name = soup.find('meta', property='og:site_name')
    if og_site_name:
        return og_site_name.get('content')

    if soup.title:
        return soup.title.string
    
    h1 = soup.find('h1')
    if h1:
        return h1.get_text()
    
    return "the company"
    
def extract_keywords_from_page(soup):
    text_parts = []
    
    if soup.title and soup.title.string:
        text_parts.append(soup.title.string)
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        text_parts.append(meta_desc.get('content', ''))
    
    for tag in soup.find_all(['h1', 'h2', 'h3']):
        text_parts.append(tag.get_text())
    
    return text_parts

def get_seed_keyword(all_text_parts, company_name):
    all_text = ' '.join(all_text_parts).lower()
    words = re.findall(r'\b[a-z]+\b', all_text)  
    company_words = set(company_name.lower().split())
    filtered_words = [w for w in words if w not in STOP_WORDS and w not in company_words and len(w) > 2]  
    if not filtered_words:
        return None

    counts = Counter(filtered_words)
    top_word, top_count = counts.most_common(1)[0]
    return top_word

def get_client_context(base_url):
    sitemap_urls = get_sitemap_urls(base_url)
    pages_to_scrape = pick_pages_to_scrape(sitemap_urls, base_url)
    
    company_name = None
    all_text_parts = []
    
    for url in pages_to_scrape:
        soup = scrape_page_content(url)
        if soup is None:
            continue
        
        if company_name is None:
            company_name = get_company_name(soup)
        
        all_text_parts.extend(extract_keywords_from_page(soup))
    
    if not all_text_parts:
        return {'company_name': company_name or 'the company', 'seed_keyword': None}
    
    seed_keyword = get_seed_keyword(all_text_parts, company_name)
    
    return {
        'company_name': company_name or 'the company',
        'seed_keyword': seed_keyword
    }

if __name__ == "__main__":
    result = get_client_context("https://www.foxydigits.com")
    print(result)