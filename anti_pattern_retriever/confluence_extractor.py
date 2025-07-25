import requests
import html2text
from pathlib import Path
from configuration import Settings

MARKDOWN_DIRECTORY = Path("temp/markdown")

def _load_settings():
    settings = Settings()

    required = {
        "CONFLUENCE_BASE_URL": settings.confluence_base_url,
        "API_USERNAME": settings.api_username,
        "API_TOKEN": settings.api_token,
        "SPACE_KEY": settings.space_key
    }

    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required config: {', '.join(missing)}")

    return settings


settings = _load_settings()


def _get_auth_headers():
    return {
        "auth": (settings.api_username, settings.api_token),
        "headers": {"Accept": "application/json"}
    }

def get_all_pages():
    url = f"{settings.confluence_base_url}/rest/api/content"
    params = {
        "spaceKey": settings.space_key,
        "expand": "ancestors",
        "limit": settings.page_limit,
        "type": "page"
    }

    pages = []
    while url:
        resp = requests.get(url, **_get_auth_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        pages += [(p["id"], p["title"]) for p in data["results"]]
        next_link = data.get("_links", {}).get("next")
        url = f"{settings.confluence_base_url}{next_link}" if next_link else None
        params = {}

    return pages

def download_page_as_markdown(page_id: str, title: str):
    MARKDOWN_DIRECTORY.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(c if c.isalnum() or c in " -_." else "_" for c in title)
    md_file = MARKDOWN_DIRECTORY / f"{safe_title}.md"

    url = f"{settings.confluence_base_url}/rest/api/content/{page_id}?expand=body.storage"
    resp = requests.get(url, **_get_auth_headers())
    resp.raise_for_status()
    body = resp.json()["body"]["storage"]["value"]
    markdown = html2text.html2text(body)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{markdown}")


def export_folder_contents(parent_page_id: str):
    url = f"{settings.confluence_base_url}/rest/api/content/{parent_page_id}/descendant/page"
    params = { "limit": 100 }
    pages = []

    while url:
        resp = requests.get(url, **_get_auth_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        pages.extend([(p["id"], p["title"]) for p in data["results"]])
        next_link = data.get("_links", {}).get("next")
        url = f"{settings.confluence_base_url}{next_link}" if next_link else None
        params = {}

    for pid, title in pages:
        download_page_as_markdown(pid, title)

    print(f"Exported {len(pages)} child pages under parent ID {parent_page_id}")
