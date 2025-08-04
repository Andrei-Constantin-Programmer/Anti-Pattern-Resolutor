import requests

from setup_cli_parameters import setup_cli_argument_parser

from configuration import (
    set_api_username,
    set_api_token,
    set_confluence_base_url,
    set_space_key,
    set_output_dir,
    set_page_limit
)


# Set script configuration (ENV file), if user is using --config
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


# Lists all page titles in the given Confluence space
def _list_pages():
    from confluence_extractor import get_all_pages

    pages = get_all_pages()
    print("Available pages in the configured space:")
    for pid, title in pages:
        print(f"{pid} - {title}")
    return


# Extracts the Confluence pages as Markdown files
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


# Exports the downloaded Markdown files as JSON files
def _export_json(args):
    from json_convertor import convert_markdown_directory
    print("Exporting Markdown files to JSON.")
    convert_markdown_directory(args.default_metadata)
    print("Export finalised.")


# Debug utility to see what Confluence user is logged in (based on Confluence token)
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
    
    parser = setup_cli_argument_parser()
    args = parser.parse_args()

    if args.default_metadata and not (args.folder_id or args.page_id):
        parser.error("--default-metadata requires --folder-id or --page-id.")

    # Command-line argument priority: whoami > config > list_pages > folder_id > page_id
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
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
