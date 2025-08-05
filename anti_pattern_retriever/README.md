# Anti-Pattern Confluence to JSON Exporter

This tool extracts anti-pattern documents from Confluence Cloud and converts them into structured JSONs for use in the AntiPatternRemediator.

---

## Installation

### Requirements
Python 3.13.0 (recommended)

### Clone the repository

```bash
git clone https://github.com/Andrei-Constantin-Programmer/Legacy-Code-Migration
cd anti_pattern_confluence_exporter
```

### Install dependencies

It is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### (Linux) Keyring
If you don't have a keyring on your machine, e.g,:
```bash
keyring.errors.NoKeyringError: No recommended backend was available.
```

Set the keyring environment variable
```bash
echo 'export PYTHON_KEYRING_BACKEND=keyrings.alt.file.PlaintextKeyring' >> venv/bin/activate
```

## Initial configuration
Run the following command once to store your API credentials and other settings:

### Linux
```bash
python export.py --config \
  --set-username your.email@example.com \
  --set-token YOUR_CONFLUENCE_API_TOKEN \
  --set-base-url https://your-domain.atlassian.net/wiki \
  --set-space YOUR_CONFLUENCE_SPACE_KEY \
  --set-output-dir ./out
```

### Windows
```ps1
python export.py --config `
  --set-username your.email@example.com `
  --set-token YOUR_CONFLUENCE_API_TOKEN `
  --set-base-url https://your-domain.atlassian.net/wiki `
  --set-space YOUR_CONFLUENCE_SPACE_KEY `
  --set-output-dir ./out
```

- API tokens can be generated from: https://id.atlassian.com/manage/api-tokens
- The token is stored securely in your system keyring.
- Other settings are saved to a .env file in the standard OS config directory:
    - Windows: %APPDATA%\ConfluenceExporter\\.env
    - Linux: ~/.config/confluence-exporter/.env

## Usage

### Command-Line Parameters
`-h`, `--help` - Show built-in help message and exit.  
`-p`, `--page-id` - One or more specific Confluence page IDs to export.  
`--folder-id` - Export all pages under a parent page (excluding the parent itself).  
`--default-metadata` - Use default (generic) values for category, language, and severity (no prompts) when exporting to JSON.  
`--list-pages` - List all available pages with ID and title.  
`--whoami` - Show current Confluence user.  
`--config`- Override .env config interactively via command-line. Ignores the aforementioned flags. Use with one or more of the config flags listed below.

#### Config Settings
_You can only use these when utilising_ `--config`:  
`--set-username` - Set and save your Confluence API username.  
`--set-token` - Set and save your Confluence API token.  
`--set-base-url` - Set and save the base Confluence URL.  
`--set-space` - Set and save the Confluence space key.  
`--set-limit` - Set and save the max number of pages to fetch.  
`--set-output-dir` - Set and save the output directory for downloaded files.  

### Examples

#### Export specific page(s) by ID

```bash
python export.py --page-id 12345678 23456789
```
**Note**: You can find page IDs by looking at the URL: `https://your-domain.atlassian.net/wiki/spaces/YOUR_CONFLUENCE_SPACE_KEY/pages/`**12345678**`/page_name`

#### Export all children under a parent (folder-like) page

```bash
python export.py --folder-id 987654321
```

#### List all pages in the configured space (for reference)

```bash
python export.py --list-pages
```

#### View current Confluence user (for debugging)

```bash
python export.py --whoami
```
