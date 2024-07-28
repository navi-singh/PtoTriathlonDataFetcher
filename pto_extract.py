import requests
import re
from bs4 import BeautifulSoup

# URL of the webpage to fetch
urls = ['https://stats.protriathletes.org/rankings/men',
        'https://stats.protriathletes.org/rankings/women']

NUMBER_OF_ATHLETES = 5
BASE_URL = 'https://stats.protriathletes.org'


def extract_height(height_str):
    match = re.search(r"(\d+\.\d+)", height_str)
    if match:
        return float(match.group(1))
    return float('inf')  # Return infinity if no height is found


def extract_athlete_data(link, athlete_info):
    athlete_response = requests.get(BASE_URL + link)
    if athlete_response.status_code == 200:
        athlete_result = BeautifulSoup(
            athlete_response.content, 'html.parser')

        name = athlete_result.find(
            'h2', class_='font-weight-bold text-uppercase mb-0 headline')
        if name:
            athlete_info['Name'] = name.text.strip()
        attributes = athlete_result.find('div', class_='info').find_all(
            'div', class_='attribute')
        for attribute in attributes:
            attr_name = attribute.find('div', class_='name')
            attr_value = attribute.find('div', class_='value')
            if attr_name and attr_value:
                athlete_info[attr_name.text.strip(
                )] = attr_value.text.strip()
        print('*', end='', flush=True)


def print_athletes_data(athletes, sort_by='Rank'):
    sorted_athletes = sorted(
        athletes, key=lambda x: extract_height(x[sort_by]))

    max_name_length = max(
        len('Name'), *(len(athlete['Name']) for athlete in athletes))
    max_age_length = max(
        len('Age'), *(len(athlete['Age']) for athlete in athletes))
    max_height_length = max(
        len('Height'), *(len(athlete['Height']) for athlete in athletes))
    max_rank_length = max(len('Rank'), *(len(str(athlete['Rank']))
                          for athlete in athletes))

    print(
        f"{'Name'.ljust(max_name_length)} "
        f"{'Age'.ljust(max_age_length)} "
        f"{'Height'.ljust(max_height_length)} "
        f"{'Rank'.ljust(max_rank_length)}"
    )
    for athlete in sorted_athletes:
        print(
            f"{athlete['Name'].ljust(max_name_length)} "
            f"{athlete['Age'].ljust(max_age_length)} "
            f"{athlete['Height'].ljust(max_height_length)} "
            f"{str(athlete['Rank']).ljust(max_rank_length)}"
        )


def fetch_athletes(url):
    response = requests.get(url)
    athletes = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        trows = soup.find_all('div', class_='trow')
        trows = trows[:NUMBER_OF_ATHLETES]

        for trow in trows:
            ranking_number_div = trow.find('div', class_='ranking-number')
            if ranking_number_div:
                ranking_number = ranking_number_div.text.strip()
                a_tag = trow.find('a', class_='athlete-pic-group undefined')
                if a_tag and 'href' in a_tag.attrs:
                    href = a_tag['href']
                    athlete_info = {}
                    athlete_info['Rank'] = ranking_number
                    extract_athlete_data(href, athlete_info)
                athletes.append(athlete_info)
        print()
        print_athletes_data(athletes)

    else:
        print(
            f"Failed to retrieve the page. Status code: {response.status_code}")


for url in urls:
    print(f"Fetching data from {url}")
    fetch_athletes(url)
