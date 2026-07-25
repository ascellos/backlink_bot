import requests
import whois
from datetime import datetime

def check_site_trust(url: str):
    result = {
        "url": url,
        "loads_successfully": False,
        "uses_https": url.startswith("https://"),
        "domain_age_years": None,
        "status": "unknown"
    }

    try:
        response = requests.get(url, timeout=10)
        result["loads_successfully"] = response.status_code == 200
    except requests.exceptions.RequestException:
        result["loads_successfully"] = False

    try:
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            if creation_date.tzinfo is not None:
                creation_date = creation_date.replace(tzinfo=None)
            age_years = (datetime.now() - creation_date).days / 365
            result["domain_age_years"] = round(age_years, 1)
    except Exception as e:
        print("DEBUG - WHOIS error:", e)
        result["domain_age_years"] = None

    if result["loads_successfully"] and result["uses_https"] and (result["domain_age_years"] or 0) >= 2:
        result["status"] = "trustworthy"
    elif result["loads_successfully"]:
        result["status"] = "usable"
    else:
        result["status"] = "unreachable"

    return result