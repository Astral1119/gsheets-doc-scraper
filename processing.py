import os
import re
from tqdm import tqdm

def fix_links():
    """
    Make the links in the parsed markdown files into wikilinks.
    """
    # get the list of files in the docs directory
    files = os.listdir('parsed')

    # regex to match the links
    link_regex = re.compile(r'\[(.*?)\]\((.*?)\)')

    valid_names = [ file[:-3] for file in files ]

    for file in tqdm(files, desc='Fixing links'):
        filepath = f'parsed/{file}'

        # read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # replace the links with wikilinks if they match the pattern
        def replacer(match):
            name, url = match.groups()

            if url.startswith('//'):
                # add https: to the URL
                url = 'https:' + url

                return f'[{name}]({url})'

            elif url.startswith('/'):
                cleaned_name = name.replace('`', '')

                # remove the ' function' part from the name if it exists
                cleaned_name = re.sub(r' function$', '', cleaned_name)

                if cleaned_name in valid_names:
                    return f'[[{cleaned_name}]]'
                else:
                    return f'[{name}](https://support.google.com{url})'
            elif url.startswith('http'):
                cleaned_name = name.replace('`', '')
                cleaned_name = re.sub(r' function$', '', cleaned_name)

                if cleaned_name in valid_names:
                    return f'[[{cleaned_name}]]'
                else:
                    return f'[{name}]({url})'

            return match.group(0)

        # apply the replacement
        content = link_regex.sub(replacer, content)

        # write the updated content back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def fix_errors():
    """
    Fix Google Sheets errors (i.e. #REF!, #N/A, etc.) in the parsed markdown files by making them inline code (`code`).
    """
    files = os.listdir('parsed')

    def fix_error_helper(text):
        # regex to detect inline code blocks
        # first group = inline, second group = normal
        pattern = r'(`[^`]*`)|([^`]+)'

        # regex to match Google Sheets errors
        # does not include if it is inside a code block
        error_regex = re.compile(r'(?<!`)(#NULL!|#DIV/0!|#VALUE!?|#REF!|#NAME?|#NUM!?|#N/A|#ERROR)(?!`)')

        new_text = ''

        parts = re.findall(pattern, text)

        for code, normal in parts:
            if code:
                new_text += code
            elif normal:
                fixed = error_regex.sub(r'`\1`', normal)
                new_text += fixed

        return new_text

    for file in tqdm(files, desc='Fixing errors'):
        filepath = f'parsed/{file}'

        # read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        content = fix_error_helper(content)

        # write the updated content back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    fix_links()
    fix_errors()
