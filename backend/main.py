import os
from fastapi import FastAPI
from content_checker import check_content_similarity
from database import init_db, save_backlink, get_all_backlinks, update_backlink_status, get_backlink_by_id, count_todays_backlinks, get_anchor_history, check_anchor_diversity, add_client, get_all_clients, generate_client_report, get_previous_articles
from pydantic import BaseModel
from link_checker import verify_backlink
from article_generator import generate_article
from poster import post_to_devto
from wordpress_poster import post_to_wordpress
from database import init_db, save_backlink, get_all_backlinks
from apscheduler.schedulers.background import BackgroundScheduler
from site_checker import check_site_trust
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArticleRequest(BaseModel):
    client_site: str
    target_site: str
    niche: str

class PublishRequest(BaseModel):
    title: str
    body_markdown: str
    tags: list[str] = []

class AutoPublishRequest(BaseModel):
    client_site: str
    target_site: str
    niche: str
    title: str
    tags: list[str] = []


class WordPressPublishRequest(BaseModel):
    title: str
    content_html: str

class WPAutoPublishRequest(BaseModel):
    client_site: str
    target_site: str
    niche: str
    title: str
    anchor_text: str = None

class ClientRequest(BaseModel):
    name: str
    site_url: str
    niche: str

class SiteCheckRequest(BaseModel):
    url: str



@app.get("/")
def read_root():
    return {"message": "Backlink Bot API is running"}

@app.post("/generate-article")
def create_article(request: ArticleRequest):
    article = generate_article(request.client_site, request.target_site, request.niche)
    return {"article": article}

@app.post("/publish-devto")
def publish_article(request: PublishRequest):
    result = post_to_devto(request.title, request.body_markdown, request.tags)
    return {"published_url": result.get("url"), "raw_response": result}

@app.post("/generate-and-publish")
def generate_and_publish(request: AutoPublishRequest):
    article = generate_article(request.client_site, request.target_site, request.niche)
    result = post_to_devto(request.title, article, request.tags)
    return {"published_url": result.get("url"), "article": article}

@app.post("/publish-wordpress")
def publish_to_wordpress(request: WordPressPublishRequest):
    site_url = os.getenv("WP_SITE_URL")
    username = os.getenv("WP_USERNAME")
    app_password = os.getenv("WP_APP_PASSWORD")
    result = post_to_wordpress(site_url, username, app_password, request.title, request.content_html)
    return {"published_url": result.get("link"), "raw_response": result}

@app.post("/generate-and-publish-wp")
def generate_and_publish_wp(request: WPAutoPublishRequest):
    todays_count = count_todays_backlinks(request.client_site)
    if todays_count >= 2:
        return {
            "error": "Daily backlink limit reached for this client.",
            "client_site": request.client_site,
            "todays_count": todays_count,
            "limit": 2
        }

    if request.anchor_text:
        repeat_count = check_anchor_diversity(request.client_site, request.anchor_text)
        if repeat_count > 0:
            return {
                "warning": "This anchor text has already been used for this client.",
                "client_site": request.client_site,
                "anchor_text": request.anchor_text,
                "times_used_before": repeat_count,
                "suggestion": "Try a different anchor phrase for better link diversity."
            }

    article_markdown = generate_article(
        request.client_site, 
        request.target_site, 
        request.niche, 
        anchor_text=request.anchor_text
    )

    previous_articles = get_previous_articles(request.client_site)
    similarity_check = check_content_similarity(article_markdown, previous_articles)
    if similarity_check["is_duplicate"]:
        return {
            "warning": "Generated article is too similar to a previous one for this client.",
            "client_site": request.client_site,
            "similarity_score": similarity_check["highest_similarity"],
            "suggestion": "Try regenerating with a different angle or topic."
        }

    site_url = os.getenv("WP_SITE_URL")
    username = os.getenv("WP_USERNAME")
    app_password = os.getenv("WP_APP_PASSWORD")
    result = post_to_wordpress(site_url, username, app_password, request.title, article_markdown)

    save_backlink(
        client_site=request.client_site,
        target_site=request.target_site,
        platform="wordpress",
        published_url=result.get("link"),
        anchor_text=request.anchor_text or "AI-chosen (not specified)",
        article_content=article_markdown
    )

    return {
        "published_url": result.get("link"),
        "article": article_markdown
    }

@app.get("/backlinks")
def list_backlinks():
    rows = get_all_backlinks()
    return {"backlinks": rows}


@app.post("/verify-backlinks")
def verify_all_backlinks():
    all_links = get_all_backlinks()
    results = []
    
    for link in all_links:
        backlink_id = link[0]
        client_site = link[1]
        published_url = link[4]
        
        status = verify_backlink(published_url, client_site)
        update_backlink_status(backlink_id, status)
        
        results.append({
            "id": backlink_id,
            "published_url": published_url,
            "status": status
        })
    
    return {"checked": len(results), "results": results}

def scheduled_verification():
    print("Running scheduled backlink verification...")
    all_links = get_all_backlinks()
    for link in all_links:
        backlink_id = link[0]
        client_site = link[1]
        published_url = link[4]
        status = verify_backlink(published_url, client_site)
        update_backlink_status(backlink_id, status)
    print(f"Scheduled check complete. {len(all_links)} backlinks checked.")

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_verification, 'interval', hours = 24)  # runs once a day
scheduler.start()

@app.get("/anchor-history")
def anchor_history(client_site: str):
    history = get_anchor_history(client_site)
    return {"client_site": client_site, "anchor_history": history}

@app.post("/add-client")
def create_client(request: ClientRequest):
    success = add_client(request.name, request.site_url, request.niche)
    if success:
        return {"message": "Client added successfully", "name": request.name, "site_url": request.site_url}
    else:
        return {"error": "A client with this site URL already exists."}

@app.get("/clients")
def list_clients():
    rows = get_all_clients()
    return {"clients": rows}

@app.get("/client-report")
def client_report(client_site: str):
    report = generate_client_report(client_site)
    return report

@app.post("/check-site")
def check_site(request: SiteCheckRequest):
    return check_site_trust(request.url)

  