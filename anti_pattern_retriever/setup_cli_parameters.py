import argparse

def setup_cli_argument_parser():
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

    return parser