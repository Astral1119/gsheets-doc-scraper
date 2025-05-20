from bs4 import BeautifulSoup
import requests

fx_list_url = 'https://support.google.com/docs/table/25273'

def get_fx_list():
    """
    Scrape the urls of the functions from the Google Docs support page.
    """
    # fetch the page content
    response = requests.get(fx_list_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # links are of the form:
    # <a href="/docs/answer/3267036" target="_blank" rel="noopener">Learn more</a>

    fx_list = []
    for link in soup.find_all('a', href=True):
        if '/docs/answer/' in link['href']:
            # some links are absolute, some are relative, and some have query params
            # so we need to convert them to absolute links
            if link['href'].startswith('/'):
                link['href'] = 'https://support.google.com' + link['href']

            # remove the query params
            if '?' in link['href']:
                link['href'] = link['href'].split('?')[0]

            fx_list.append(link['href'])

            # remove duplicates
            fx_list = list(set(fx_list))

    return fx_list

from markdownify import markdownify as md

def parse_fx_to_md(fx_list):
    """
    Parse the functions to markdown format.
    """
    for fx in fx_list:
        # fetch the page content
        response = requests.get(fx)
        soup = BeautifulSoup(response.content, 'html.parser')

        # article in section article-container
        article = soup.find('section', class_='article-container')

        # convert the article to markdown
        md_content = md(str(article))

        # get the title of the article (i.e. the function name)
        title = soup.find('h1').text

        # write the content to a file
        with open(f'docs/{title}.md', 'w') as f:
            f.write(md_content)

if __name__ == '__main__':
    fx_list = get_fx_list()
    parse_fx_to_md(fx_list)
    print('Done!')

