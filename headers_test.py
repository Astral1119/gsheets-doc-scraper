"""utility to analyze headers in markdown files."""

import os


PARSED_DIR = 'parsed'


def get_unique_headers():
    """gets the unique headers from the md files in the 'parsed' directory.
    then sorts them by count and writes them to 'headers.txt'.
    """
    headers = {}

    # iterate through all files in the parsed directory
    for filename in os.listdir(PARSED_DIR):
        if filename.endswith('.md'):
            with open(os.path.join(PARSED_DIR, filename), 'r', encoding='utf-8') as file:
                for line in file:
                    if line.startswith('#'):
                        header = line.lstrip('#').strip()
                        headers[header] = headers.get(header, 0) + 1

    # sort headers by count
    sorted_headers = sorted(headers.items(), key=lambda item: item[1], reverse=True)

    # write to headers.txt
    with open('headers.txt', 'w', encoding='utf-8') as output_file:
        for header, count in sorted_headers:
            output_file.write(f"{header} - {count}\n")


def check_for_headers(headers):
    """looks at all the files in the 'parsed' directory and checks if they have
    certain headers.
    """
    files = os.listdir(PARSED_DIR)
    missing_headers = {}

    for filename in files:
        if filename.endswith('.md'):
            with open(os.path.join(PARSED_DIR, filename), 'r', encoding='utf-8') as file:
                temp = headers

                for line in file:
                    if line.startswith('#'):
                        header = line.lstrip('#').strip()
                        temp = temp.difference({header})

                if temp:
                    missing_headers[filename] = temp

    with open('missing_headers.txt', 'w', encoding='utf-8') as output_file:
        for filename, missing in missing_headers.items():
            output_file.write(f"{filename} - {\", \".join(missing)}\n")


if __name__ == "__main__":
    headers = {"Syntax"}
    check_for_headers(headers)
