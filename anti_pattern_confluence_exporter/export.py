import argparse

import requests
from configuration import (
    set_api_username,
    set_api_token,
    set_confluence_base_url,
    set_space_key,
    set_output_dir,
    set_page_limit
)

def _set_config(args):
    if args.set_username:
        set_api_username(args.set_username)
    if args.set_token:
        set_api_token(args.set_token)
    if args.set_base_url:
        set_confluence_base_url(args.set_base_url)
    if args.set_space:
        set_space_key(args.set_space)
    if args.set_limit:
        set_page_limit(args.set_limit)
    if args.set_output_dir:
        set_output_dir(args.set_output_dir)

    print("Configuration updated via command line.")

def _list_pages():
    from confluence_extractor import get_all_pages

    pages = get_all_pages()
    print("Available pages in the configured space:")
    for pid, title in pages:
        print(f"{pid} - {title}")
    return

def _extract_markdown(args):
    from confluence_extractor import download_page_as_markdown, MARKDOWN_DIRECTORY
    
    if args.folder_id:
        from confluence_extractor import export_folder_contents
        export_folder_contents(args.folder_id)
        return

    if args.page_id:
        page_count = len(args.page_id)
        for _, pid in enumerate(args.page_id):
            title = f"page_{pid}"
            download_page_as_markdown(pid, title)
        if (page_count == 1):
            print(f"Downloaded page {args.page_id[0]} to the '{MARKDOWN_DIRECTORY}' directory.")
        else:
            print(f"Downloaded {page_count} pages to the '{MARKDOWN_DIRECTORY}' directory.")
    else:
        print("No page IDs provided.")

def _whoami():
    from confluence_extractor import _get_auth_headers, settings
    url = f"{settings.confluence_base_url}/rest/api/user/current"
    resp = requests.get(url, **_get_auth_headers())
    if resp.ok:
        print("Authenticated as:", resp.json().get("displayName", "Unknown"))
    else:
        print(f"Auth failed: {resp.status_code}")
        print(resp.text)

def main():
    parser = argparse.ArgumentParser(
        description="Export Confluence pages to Markdown."
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Override .env config via command-line and exit. Ignores non-config parameters."
    )
    parser.add_argument(
        "-p", "--page-id",
        nargs="+",
        help="One or more specific Confluence page IDs to export."
    )
    parser.add_argument(
        "--folder-id",
        help="Export all pages under a parent page (like a folder), excluding the parent itself. Ignores --page-id."
    )
    parser.add_argument(
        "--list-pages",
        action="store_true",
        help="List all available pages with ID and title. Ignores --page-id and --folder-id."
    )
    parser.add_argument(
        "--whoami", 
        action="store_true", 
        help="Print current Confluence user. Ignores all other parameters."
    )

    parser.add_argument("--set-username", help="Set and save your Confluence API username.")
    parser.add_argument("--set-token", help="Set and save your Confluence API token.")
    parser.add_argument("--set-base-url", help="Set and save the base Confluence URL.")
    parser.add_argument("--set-space", help="Set and save the Confluence space key.")
    parser.add_argument("--set-limit", help="Set and save the max number of pages to fetch.")
    parser.add_argument("--set-output-dir", help="Set and save the output directory for downloaded files.")

    args = parser.parse_args()

    if args.whoami:
        _whoami()
        return
    
    if args.config:
        _set_config(args)
        return
    
    if args.list_pages:
        _list_pages()
        return

    _extract_markdown(args)


if __name__ == "__main__":
    main()
