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
from json_convertor import convert_markdown_directory

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


def _export_json(args):
    print("Exporting Markdown files to JSON.")
    convert_markdown_directory(args.default_metadata)
    print("Export finalised.")


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
    parser = argparse.ArgumentParser(description="Export Confluence pages to JSON.")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--config",
        action="store_true",
        help="Enter configuration mode: allows updating credentials and settings interactively via command-line."
    )
    mode.add_argument(
        "--list-pages",
        action="store_true",
        help="List all pages in the configured Confluence space (title and ID)."
    )
    mode.add_argument(
        "--whoami",
        action="store_true",
        help="Print the current authenticated Confluence user (for debugging)."
    )
    mode.add_argument(
        "-p", "--page-id",
        nargs="+",
        help="Export one or more specific Confluence page IDs."
    )
    mode.add_argument(
        "--folder-id",
        help="Export all child pages under a given parent page ID (excluding the parent itself)."
    )

    parser.add_argument(
        "--default-metadata",
        action="store_true",
        help="Skip metadata prompts when exporting to JSON. Uses default values."
    )

    config_group = parser.add_argument_group("Configuration Overrides (only valid with --config)")
    config_group.add_argument("--set-username", help="Set your Confluence API username.")
    config_group.add_argument("--set-token", help="Set your Confluence API token.")
    config_group.add_argument("--set-base-url", help="Set the base URL for your Confluence site.")
    config_group.add_argument("--set-space", help="Set the Confluence space key to operate within.")
    config_group.add_argument("--set-limit", help="Set the maximum number of pages to fetch when listing.")
    config_group.add_argument("--set-output-dir", help="Set the output directory for exported Markdown/JSON files.")

    args = parser.parse_args()

    if args.default_metadata and not (args.folder_id or args.page_id):
        parser.error("--default-metadata requires --folder-id or --page-id.")

    if args.whoami:
        _whoami()
        return
    
    if args.config:
        _set_config(args)
        return
    
    if args.list_pages:
        _list_pages()
        return

    if args.page_id or args.folder_id:
        _extract_markdown(args)
        _export_json(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
