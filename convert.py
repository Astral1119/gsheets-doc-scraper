from bs4 import BeautifulSoup, Tag
import requests
from tqdm import tqdm

from markdownify import markdownify as md
from markdownify import MarkdownConverter

import os

class CustomMarkdownConverter(MarkdownConverter):
    """
    Custom markdown converter to handle specific HTML tags.
    """
    def convert_iframe(self, el, text, parent_tags):
        """
        iframes should be passed through as raw HTML.
        """
        # pass through the raw HTML for iframes
        # but first, make sure that the src is absolute
        # because some are missing 'https:'
        src = el.get('src', '')
        if src and not src.startswith(('http://', 'https://')):
            src = 'https:' + src
        el['src'] = src

        # return the raw HTML as a string
        return str(el)
    
    def convert_table(self, el, text, parent_tags):
        """
        Custom table converter to automatically detect header rows.
        """
        # first, remove the class attribute
        el.attrs.pop('class', None)

        # then, convert the table to markdown
        table_md = md(str(el))

        # check row 3
        # split into columns
        rows = table_md.split('\n')

        if len(rows) > 2:
            columns = rows[2].split('|')

            # strip whitespace from columns
            columns = [col.strip() for col in columns]

            # filter out empty columns
            columns = [col for col in columns if col]
            
            # check if the columns are all bold (i.e. **bold**)
            if all(col.startswith('**') and col.endswith('**') for col in columns):
                # remove the bold formatting
                columns = [col[2:-2] for col in columns]
                # rejoin the columns
                rows[2] = '| ' + ' | '.join(columns) + ' |'
                rows[1] = '| ' + ' | '.join(['---'] * len(columns)) + ' |'
                
                # this then becomes the header row
                rows = [rows[2]] + [rows[1]] + rows[3:]
                return '\n'.join(rows) + '\n\n'
            else:
                # if not, just return the table as is
                return table_md + '\n\n'
        else:
            # if there are not enough rows, just return the table as is
            return table_md + '\n\n'


def get_fx_tags():
    """
    Gets the tags from function_tags.csv and returns a dictionary.
    """
    fx_tags = {}
    with open('function_tags.csv', 'r') as f:
        for line in f:
            fx, tag = line.strip().split(',')
            fx_tags[fx] = tag.lower()

    return fx_tags

def parse_fx_to_md():
    """
    Parse the functions to markdown format.
    """
    # ensure the parsed directory exists
    if not os.path.exists('parsed'):
        os.makedirs('parsed')

    # get the tags
    fx_tags = get_fx_tags()

    # iterate over all of the raw html in the raw directory
    # and convert them to markdown
    for fx_file in tqdm(os.listdir('raw'), desc='Parsing functions'):
        # get the name
        name = os.path.splitext(fx_file)[0]
        
        # get the raw html content
        with open(f'raw/{fx_file}', 'r') as f:
            response = requests.Response()
            response._content = f.read().encode('utf-8')

        soup = BeautifulSoup(response.content, 'html.parser')

        # article in section article-container
        article = soup.find('section', class_='article-container')

        # convert the article to markdown
        converter = CustomMarkdownConverter(code_language = "gse")
        md_content = converter.convert(str(article))

        # remove the first three lines
        md_content = '\n'.join(md_content.split('\n')[3:])

        # add tag frontmatter
        md_content = f'---\ntags:\n  - function\n  - generated\n  - {fx_tags.get(name, "unknown")}\n---\n\n' + md_content

        # write the content to a file
        with open(f'parsed/{name}.md', 'w') as f:
            f.write(md_content)

if __name__ == '__main__':
    parse_fx_to_md()
    print('Done!')
