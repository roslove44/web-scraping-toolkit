import os
import csv
from bs4 import BeautifulSoup
import requests
import re
import math

main_categories = [ 
    {"id": 1, "category": "Elevage, incubation volaille", "parent_id": None, "link": "https://www.pro-elevage.com/153-elevage-incubation-volaille"},
    {"id": 2, "category": "Grillage et Gabions", "parent_id": None, "link": "https://www.pro-elevage.com/154-grillage-gabion"},
    {"id": 3, "category": "Agriculture / Équestre - Recyclée", "parent_id": None, "link": "https://www.pro-elevage.com/155-agriculture-equestre-recyclee"},
    {"id": 4, "category": "Clôture Electrique", "parent_id": None, "link": "https://www.pro-elevage.com/150-cloture-electrique"},
]

categories = []
visited_links = set()
current_id = 5

product_id = 1
products = []

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


def get_products(category):
    url = category['link']
    soup = extract_soup(url)
    if not soup:
        print(f"❌ Erreur : impossible de récupérer la page {url}")
        return

    total_products_soup = soup.find('div', class_='col-lg-5 total-products')
    if not total_products_soup:
        print(f"⚠️ Impossible de trouver le nombre total de produits sur {url}")
        return

    total_products_text = total_products_soup.find('p').get_text(strip=True) if total_products_soup.find('p') else ""
    match = re.search(r'\d+', total_products_text)
    total_products = int(match.group()) if match else 0

    if total_products == 0:
        print(f"⚠️ Aucun produit trouvé sur {url}")
        return

    max_page = math.ceil(total_products / 50)
    print(f"📊 {total_products} produits trouvés sur {max_page} pages.")
    if max_page >= 1:
        for page in range(1, max_page + 1):
            page_url = f'{url}?page={page}'
            get_one_page_products(page_url, category['id'])

def get_one_page_products(page_url, category_id):
    global product_id
    print(f"📂 Scraping en cours : {page_url}")
    current_soup = extract_soup(page_url)
    products_container = current_soup.find_all('div', class_='innovatoryProductGrid')[0].find_all('article', class_='js-product-miniature')
    if not products_container:
        print(f"Aucun produit trouvé sur la page : {page_url}")
        return
    for product in products_container:
        # Image du produit
        product_image_tag = product.find('span', class_='cover_image')
        product_image = product_image_tag.find('img').get('src') if product_image_tag and product_image_tag.find('img') else None

        # Lien du produit
        product_link_tag = product.find('div', class_='innovatoryProduct-image')
        product_link = product_link_tag.find('a').get('href') if product_link_tag and product_link_tag.find('a') else None

        # Nom du produit
        product_title_tag = product.find('h2', class_='productName')
        product_title = product_title_tag.find('a').get_text(strip=True) if product_title_tag and product_title_tag.find('a') else "N/A"

        # Prix du produit
        product_price_tag = product.find('span', class_='price')
        product_price = product_price_tag.get_text(strip=True) if product_price_tag else "N/A"

        products.append({"id": product_id, "name": product_title, "price": product_price, "image_src": product_image, "category_id": category_id, "link": product_link})
        product_id += 1


def set_products_file():
    csv_filename = "categories_all.csv"
    input_dir = "result/pro-elevage"
    file_path = os.path.join(input_dir, csv_filename)
    categories = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            categories.append(row)
        print("End Reconstitution des catégories")

    # Scraping des produits
    for category in categories:
        get_products(category)
    
    csv_filename = "products_all.csv"
    output_dir = "result/pro-elevage"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, csv_filename), mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name", "price", "image_src", "category_id", "link"])
        writer.writeheader()
        writer.writerows(products)
    print(f"Export terminé : {csv_filename}")

set_products_file()