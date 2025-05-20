import os
import re

# for each file in docs/
# for each link that leads to (/docs/answer/)
# replace the link (in the form [name](link)) with a simple wikilink, i.e. [[name]]
# also strip backticks from name in the wikilink
def fix_links():
    """
    Fix the links in the markdown files.
    """
    # get the list of files in the docs directory
    files = os.listdir('docs')

    # regex to match the links
    link_regex = re.compile(r'\[(.*?)\]\((.*?)\)')

    for file in files:
        filepath = f'docs/{file}'

        # read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # replace the links with wikilinks if they match the pattern
        def replacer(match):
            name, url = match.groups()
            if '/docs/answer/' in url:
                cleaned_name = name.replace('`', '')
                # remove the ' function' part from the name if it exists
                cleaned_name = re.sub(r' function$', '', cleaned_name)
                return f'[[{cleaned_name}]]'
            return match.group(0)

        # apply the replacement
        content = link_regex.sub(replacer, content)

        # write the updated content back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def remove_titles():
    """
    Remove the titles and the header line (e.g. ===...) from the markdown files.
    """
    # get the list of files in the docs directory
    files = os.listdir('docs')

    for file in files:
        filepath = f'docs/{file}'

        # read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.readlines()

        # remove the first three lines
        content = content[3:]

        # write the updated content back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(content)

def normalize_file_names():
    """
    If the second word in the file name is 'function', remove it.
    """
    files = os.listdir('docs')
    for file in files:
        # regex to check if the second word is 'function'
        if re.match(r'^[.a-zA-Z]+ function', file):
            new_name = file.replace(' function', '')
            os.rename(f'docs/{file}', f'docs/{new_name}')

if __name__ == '__main__':
    fix_links()
    remove_titles()
    normalize_file_names()
    print("Links fixed.")
