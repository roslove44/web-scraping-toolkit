import os
import csv
from bs4 import BeautifulSoup
import requests

main_categories = [ 
    {"id": 1, "category": "Elevage, incubation volaille", "parent_id": None, "link": "https://www.pro-elevage.com/153-elevage-incubation-volaille"},
    {"id": 2, "category": "Grillage et Gabions", "parent_id": None, "link": "https://www.pro-elevage.com/154-grillage-gabion"},
    {"id": 3, "category": "Agriculture / Équestre - Recyclée", "parent_id": None, "link": "https://www.pro-elevage.com/155-agriculture-equestre-recyclee"},
    {"id": 4, "category": "Clôture Electrique", "parent_id": None, "link": "https://www.pro-elevage.com/150-cloture-electrique"},
]

categories = []
visited_links = set()
current_id = 5


def extract_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "html.parser")
    else:
        print(f"Erreur {response.status_code} en accédant à {url}")
        return None


def get_title(soup):
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return 'N/A'


def get_sub_categories(url, categories, parent_id):
    global current_id

    soup = extract_soup(url)
    if not soup:
        return

    parent_title = get_title(soup)
    
    ul_category = soup.find('ul', id='categoryList')
    if not ul_category:
        print(f"Aucune liste de catégories trouvée sur {parent_title}")
        return

    li_category = ul_category.find_all('li', class_='CategoryCarousel-carouselItem')

    for li in li_category:
        a_tag = li.find('a')
        if a_tag and 'href' in a_tag.attrs:
            link = a_tag['href']
            title = a_tag['title']
            categories.append({"id": current_id, "category": title, "parent_id": parent_id, "link": link})
            current_id += 1

def get_categories_recursively(url, categories, parent_id):
    global current_id

    if url in visited_links:
        return
    visited_links.add(url)

    soup = extract_soup(url)
    if not soup:
        return

    parent_title = get_title(soup)
    
    ul_category = soup.find('ul', id='categoryList')
    if not ul_category:
        print(f"⚠️ Aucune liste de catégories trouvée sur {parent_title}")
        return

    li_category = ul_category.find_all('li', class_='CategoryCarousel-carouselItem')

    for li in li_category:
        a_tag = li.find('a')
        if a_tag and 'href' in a_tag.attrs:
            link = a_tag['href']
            title = a_tag.get('title', 'Sans titre')

            # Ajouter la catégorie
            categories.append({"id": current_id, "category": title, "parent_id": parent_id, "link": link})
            new_parent_id = current_id
            current_id += 1

            get_categories_recursively(link, categories, new_parent_id)


def set_categories_file(main_categories, categories):
    for category in main_categories:
            get_categories_recursively(category['link'], categories, category['id'])
    
    csv_filename = "categories_all.csv"

    output_dir = "result/pro-elevage"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, csv_filename), mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "category", "parent_id", "link"])
        writer.writeheader()
        writer.writerows(main_categories)
        writer.writerows(categories)
    print(f"Export terminé : {csv_filename}")

set_categories_file(main_categories, categories)