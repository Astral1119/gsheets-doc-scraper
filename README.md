# Google Sheets Formula Documentation Scraper (GSFDS)
These scripts scrape Google Sheets formula documentation from the official Google support page and parse it to Markdown format.

# Repository Structure
1. `README.md`, `requirements.txt`, `.gitignore`: Standard files for documentation, dependencies, and ignored files.
2. `raw_scrape.py`: Contains the main scraping logic to fetch the HTML content from the Google support page.
3. `convert.py`: Contains the logic to parse the scraped HTML content and convert it into Markdown format.
4. `process.py`: Takes the Markdown content and processes it to generate the final output.
5. `update.py`: A helper script to update the community documentation with the latest scraped data. Still in development.
6. `function_tags.csv`: A CSV file containing function tags used in the scraping process, generated using `IMPORTHTML` in Google Sheets.

# Usage
1. Set up a Python environment and install the required dependencies using:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the scraping script to fetch the latest documentation:
   ```bash
    python3 raw_scrape.py && python3 convert.py && python3 process.py
    ```
