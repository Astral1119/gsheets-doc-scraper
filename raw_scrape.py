"""scrape google sheets formula documentation from the support page."""

import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


FX_LIST_URL = 'https://support.google.com/docs/table/25273'


def get_fx_list():
    """scrape the urls of the functions from the google docs support page."""
    # fetch the page content
    response = requests.get(FX_LIST_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    # manually added function urls not in the table
    fx_list = [
        'https://support.google.com/docs/answer/15820999',
        'https://support.google.com/docs/answer/12406049',
        'https://support.google.com/docs/answer/9982776',
        'https://support.google.com/docs/answer/9584429',
        'https://support.google.com/docs/answer/9983035',
    ]
    fx_tags = ['']
    fx_names = [
        'AI',
        'XMATCH',
        'BINOM.DIST.RANGE',
        'COUNTUNIQUEIFS',
        'PERCENTIF',
    ]

    # all links are within a table (tbody)
    # columns are fx type, fx name, fx syntax, fx description
    # link to full documentation is in the description with a 'learn more' link
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
    """get the raw html files for the functions.

    parameters:
        fx_list (list[str]): list of urls to fetch.
        fx_tags (list[str]): list of function tags/categories.
        fx_names (list[str]): list of function names.
        skip_existing (bool): if true, skip downloading files that already exist.
    """
    out_dir = 'raw'
    os.makedirs(out_dir, exist_ok=True)

    for fx, tag, name in tqdm(zip(fx_list, fx_tags, fx_names), total=len(fx_list), desc='downloading'):
        filename = f"{name.replace(' ', '_').replace('/', '-')}.html"
        filepath = os.path.join(out_dir, filename)

        if skip_existing and os.path.exists(filepath):
            continue

        response = requests.get(fx)
        if response.status_code == 200:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(response.text)
        else:
            print(f"failed to fetch {name} ({fx}): {response.status_code}")


if __name__ == "__main__":
    fx_list, fx_tags, fx_names = get_fx_list()
    get_raw_files(fx_list, fx_tags, fx_names)
