import os
import sys

def get_unique_headers():
    """
    gets the unique headers from the md files in the 'parsed' directory.
    then sorts them by count and writes them to 'headers.txt'.
    """
    headers = {}
    parsed_dir = 'parsed'

    # iterate through all files in the parsed directory
    for filename in os.listdir(parsed_dir):
        if filename.endswith('.md'):
            with open(os.path.join(parsed_dir, filename), 'r', encoding='utf-8') as file:
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

if __name__ == "__main__":
    get_unique_headers()
    print("Unique headers have been extracted and written to 'headers.txt'.")
