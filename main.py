import requests
from bs4 import BeautifulSoup
import re
from openpyxl import Workbook

def get_total_pages(url):
    response = requests.get(url)
    doc = BeautifulSoup(response.content, 'html.parser')
    total_pages = int(doc.find('div', {'class': 'search_pagination_right'}).find_all('a')[-2].text)
    return total_pages

def extract_game_info(game):
    name = game.find('span', {'class': 'title'}).text
    published_date = game.find('div', {'class': 'col search_released responsive_secondrow'}).text.strip()

    original_price_elem = game.find('div', {'class': 'discount_original_price'})
    original_price = original_price_elem.text.strip() if original_price_elem else 'N/A'

    discount_price_elem = game.find('div', {'class': 'discount_final_price'})
    discount_price = discount_price_elem.text.strip() if discount_price_elem else 'N/A'

    review_summary = game.find('span', {'class': 'search_review_summary'})
    reviews_html = review_summary['data-tooltip-html'] if review_summary else 'N/A'

    match = re.search(r'(\d+,*\d*)\s+user reviews', reviews_html)
    reviews_number = match.group(1).replace(',', '') if match else 'N/A'

    return name, published_date, original_price, discount_price, reviews_number

def scrape_page(url, filter, sheet):
    total_pages = get_total_pages(url)
    line_count = 0

    for page in range(1, total_pages + 1):
        response = requests.get(f"{url}&page={page}")
        doc = BeautifulSoup(response.content, 'html.parser')
        games = doc.find_all('div', {'class': 'responsive_search_name_combined'})

        for game in games:
            game_info = extract_game_info(game)
            # Write data to the Excel sheet
            sheet.append([*game_info, filter])

            line_count += 1
            if line_count > 100:
                break
        
        if line_count > 100:
            break

def main(search_filters=["topsellers"]):
    wb = Workbook()
    ws = wb.active
    ws.title = "Game Data"
    
    ws.append(['Name', 'Published Date', 'Original Price', 'Discount Price', 'Reviews', 'Search Filter'])

    for filter in search_filters:
        url = f'https://store.steampowered.com/search/?filter={filter}'
        scrape_page(url, filter, ws)

    wb.save('games_all.xlsx')

search_filters = ['topsellers', 'mostplayed', 'newreleases', 'upcomingreleases']
main(search_filters)
