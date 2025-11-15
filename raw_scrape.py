import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

fx_list_url = 'https://support.google.com/docs/table/25273'

def get_fx_list():
    """
    scrape the urls of the functions from the google docs support page.
    """
    # fetch the page content
    response = requests.get(fx_list_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # links are of the form:
    # <a href="/docs/answer/3267036" target="_blank" rel="noopener">Learn more</a>

    fx_list = [
        'https://support.google.com/docs/answer/15820999',
    ]
    fx_tags = [
        '',
    ]
    fx_names = [
        'AI'
    ]

    # all links are within a table (tbody)
    # columns are fx type, fx name, fx syntax, fx description
    # link to full documentation is in the description with a 'Learn more' link

    table_body = soup.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        fx_link = cols[3].find('a')['href']
        fx_name = cols[1].text
        # some links are relative, so we need to add the base url for the ones that start with /
        if fx_link.startswith('/'):
            fx_link = 'https://support.google.com' + fx_link

        # add to the lists
        fx_tags.append(cols[0].text)
        fx_list.append(fx_link)
        fx_names.append(fx_name)

    return fx_list, fx_tags, fx_names

def get_raw_files(fx_list, fx_tags, fx_names, skip_existing=True):
    """
    get the raw html files for the functions.
    
    parameters:
        fx_list (list[str]): List of URLs to fetch.
        fx_tags (list[str]): List of function tags/categories.
        fx_names (list[str]): List of function names.
        skip_existing (bool): If True, skip downloading files that already exist.
    """
    os.makedirs('raw', exist_ok=True)

    for fx, tag, name in tqdm(zip(fx_list, fx_tags, fx_names), total=len(fx_list)):
        filename = f"{name.replace(' ', '_').replace('/', '-')}.html"
        filepath = os.path.join('docs', filename)

        if skip_existing and os.path.exists(filepath):
            # optionally print or log skipped file
            # print(f"Skipping existing: {filename}")
            continue

        response = requests.get(fx)
        if response.status_code == 200:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(response.text)
        else:
            print(f"Failed to fetch {name} ({fx}): {response.status_code}")

if __name__ == "__main__":
    fx_list, fx_tags, fx_names = get_fx_list()
    get_raw_files(fx_list, fx_tags, fx_names)
