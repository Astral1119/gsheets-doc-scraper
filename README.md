# Google Sheets Documentation Scraper

a collection of python scripts that scrape, parse, and process google sheets formula documentation from the official google support pages.

## overview

this project automates the extraction of google sheets function documentation into markdown format, making it easier to integrate into documentation systems like obsidian or other markdown-based knowledge bases.

## features

- **scrapes** raw html documentation from google support pages
- **converts** html to clean, formatted markdown
- **processes** markdown with custom formatting rules (wikilinks, code blocks, error formatting, etc.)
- **updates** documentation intelligently while preserving manual edits

## repository structure

```
.
├── raw_scrape.py      # scrapes function documentation from google support
├── convert.py         # converts scraped html to markdown
├── processing.py      # post-processes markdown files (formatting, links, etc.)
├── update.py          # syncs updated docs while respecting manual edits
├── headers_test.py    # utility to analyze markdown headers
├── function_tags.csv  # function categories (generated via IMPORTHTML in google sheets)
├── requirements.txt   # python dependencies
├── raw/              # directory for scraped html files
└── parsed/           # directory for processed markdown files
```

## installation

1. create and activate a python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## usage

### full pipeline

to scrape, convert, and process all documentation:

```bash
python3 raw_scrape.py && python3 convert.py && python3 processing.py
```

### individual scripts

**1. scrape raw html documentation:**
```bash
python3 raw_scrape.py
```
- downloads html from google support pages
- saves to `raw/` directory
- skips existing files by default

**2. convert html to markdown:**
```bash
python3 convert.py
```
- parses html from `raw/` directory
- converts to markdown with custom converters
- adds yaml frontmatter with tags
- outputs to `parsed/` directory

**3. process markdown files:**
```bash
python3 processing.py
```
- applies formatting fixes (code blocks, headers, links)
- converts function references to wikilinks
- escapes special characters (dollar signs, errors)
- adds source attribution callouts

**4. update documentation (optional):**
```bash
python3 update.py <target_dir> <source_dir>
```
- syncs files from source to target directory
- respects files tagged with `modified` in frontmatter
- generates detailed update log

**5. analyze headers (utility):**
```bash
python3 headers_test.py
```
- finds missing headers in markdown files
- useful for quality control

## processing features

the markdown processor applies several transformations:

- **error codes**: wraps google sheets errors (`#VALUE!`, `#REF!`, etc.) in code blocks
- **code blocks**: converts inline code to fenced code blocks with `gse` language
- **wikilinks**: converts function references to obsidian-style wikilinks
- **headers**: converts setext-style headers to atx-style (`###`)
- **dollar signs**: escapes `$` to prevent latex interpretation
- **bullet lists**: standardizes bullet points to use `-` instead of `*`
- **source attribution**: adds callout linking back to original documentation

## configuration

- **function_tags.csv**: maps function names to categories
  - can be regenerated using google sheets `IMPORTHTML` function
  - format: `function_name,category`

## output format

each generated markdown file includes:

```markdown
---
tags:
  - function
  - generated
  - <category>
description: <brief description>
---

> [!INFO]
> This page was originally generated from [official documentation](<url>).

<function documentation content>
```

## development

the codebase follows these conventions:

- **lowercase docstrings and comments**: all documentation uses lowercase for consistency
- **modular functions**: each script has focused, single-purpose functions
- **descriptive variable names**: clear naming for maintainability
- **comprehensive processing**: handles edge cases in google's documentation format

## notes

- the scraper is designed specifically for google sheets function documentation
- some functions are manually added (ai, xmatch, etc.) as they may not appear in the main table
- the update script preserves files with the `modified` tag to prevent overwriting manual edits
- all scripts use utf-8 encoding to handle special characters

## license

this project is for educational and documentation purposes.
