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


def write_athletes_data_to_file(athletes, sort_by='Rank'):
    # Open the file in write mode (will create the file if it doesn't exist)
    with open('athletes.txt', 'a') as file:
        sorted_athletes = sorted(
            athletes, key=lambda x: extract_height(x[sort_by]))

        # Calculate max lengths for formatting once
        max_lengths = {
            'Name': max(len('Name'), *(len(athlete['Name']) for athlete in athletes)),
            'Age': max(len('Age'), *(len(athlete['Age']) for athlete in athletes)),
            'Height': max(len('Height'), *(len(athlete['Height']) for athlete in athletes)),
            'Rank': max(len('Rank'), *(len(str(athlete['Rank'])) for athlete in athletes))
        }

        # Prepare and write headers once
        header = (
            f"{'Name'.ljust(max_lengths['Name'])} "
            f"{'Age'.ljust(max_lengths['Age'])} "
            f"{'Height'.ljust(max_lengths['Height'])} "
            f"{'Rank'.ljust(max_lengths['Rank'])}\n"
        )
        file.write(header)
        print(header.strip())  # Strip newline when printing to console

        # Loop through and write each athlete's data
        for athlete in sorted_athletes:
            row = (
                f"{athlete['Name'].ljust(max_lengths['Name'])} "
                f"{athlete['Age'].ljust(max_lengths['Age'])} "
                f"{athlete['Height'].ljust(max_lengths['Height'])} "
                f"{str(athlete['Rank']).ljust(max_lengths['Rank'])}\n"
            )
            file.write(row)
            print(row.strip())  # Strip newline when printing to console


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
        write_athletes_data_to_file(athletes, 'Height')

    else:
        print(
            f"Failed to retrieve the page. Status code: {response.status_code}")


for url in urls:
    print(f"Fetching data from {url}")
    fetch_athletes(url)
