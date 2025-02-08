import os
import csv
from bs4 import BeautifulSoup
import requests
import re
import math

# Add csv limit to read bigger file
# import sys
# csv.field_size_limit((int )(sys.maxsize/1000000000000))

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

def get_product_description(page_url):
    current_soup = extract_soup(page_url)
    
    product_description = current_soup.select_one('#description .product-description')
    product_reference = current_soup.select_one('#product-details .product-reference span')

    return {
        "product_description": product_description if product_description else None,
        "product_reference": product_reference.get_text(strip=True) if product_reference else None
    }

def set_products_to_shopify_file():
    csv_filename = "categories_all.csv"
    input_dir = "result/pro-elevage"
    file_path = os.path.join(input_dir, csv_filename)
    categories = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            categories.append(row)
        print("End Reconstitution des catégories")
    
    product_csv_filename = "products_all.csv"
    product_file_path = os.path.join(input_dir, product_csv_filename)
    products = []
    with open(product_file_path, mode='r', newline='', encoding='utf-8') as product_file:
        reader = csv.DictReader(product_file)
        for row in reader:
            products.append(row)
        print("End Reconstitution des Produits")

    csv_filename = "products_shopify.csv"
    output_dir = "result/pro-elevage"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, csv_filename), mode='w', newline='', encoding='utf-8') as file:
        fieldnames = [
            "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published",
            "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value",
            "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty", 
            "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
            "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src", "Image Position",
            "Image Alt Text", "Gift Card", "SEO Title", "SEO Description",
            "Google Shopping / Google Product Category", "Google Shopping / Gender", "Google Shopping / Age Group",
            "Google Shopping / MPN", "Google Shopping / AdWords Grouping", "Google Shopping / AdWords Labels",
            "Google Shopping / Condition", "Google Shopping / Custom Product",
            "Google Shopping / Custom Label 0", "Google Shopping / Custom Label 1", 
            "Google Shopping / Custom Label 2", "Google Shopping / Custom Label 3", "Google Shopping / Custom Label 4",
            "Variant Image", "Variant Weight Unit", "Variant Tax Code", "Cost per item",
            "Price / International", "Compare At Price / International", "Status", "Custom Product Type"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            descriptions = get_product_description(product['link'])
            shopify_product = {
                "Handle": product['name'],
                "Title": product['name'],
                "Body (HTML)": descriptions['product_description'],
                "Vendor": None,  
                "Product Category": None,
                "Type": None,
                "Tags": categories[int(product['category_id'])-1]['category'],
                "Custom Product Type": categories[int(product['category_id'])-1]['category'],
                "Published": "TRUE",
                "Option1 Name": "",
                "Option1 Value": "",
                "Variant SKU": descriptions['product_reference'],
                "Variant Grams": "",
                "Variant Inventory Tracker": "shopify",
                "Variant Inventory Qty": 10000,
                "Variant Inventory Policy": "deny",
                "Variant Fulfillment Service": "manual",
                "Variant Price": (product['price']).replace("€", "").replace(",", ".").strip(),
                "Variant Compare At Price": None,
                "Variant Requires Shipping": "TRUE",
                "Variant Taxable": "false",
                "Variant Barcode": None,
                "Image Src": product['image_src'],
                "Image Position": "1",
                "Image Alt Text": None,
                "Gift Card": "FALSE",
                "SEO Title": product["name"],
                "SEO Description": product["name"],
                "Google Shopping / Google Product Category": categories[int(product['category_id'])-1]['category'],
                "Google Shopping / Gender": "",
                "Google Shopping / Age Group": "",
                "Google Shopping / MPN": "",
                "Google Shopping / AdWords Grouping": "",
                "Google Shopping / AdWords Labels": "",
                "Google Shopping / Condition": "New",
                "Google Shopping / Custom Product": "FALSE",
                "Variant Image": product['image_src'],
                "Variant Weight Unit": "",
                "Variant Tax Code": "",
                "Cost per item": "",
                "Price / International": "",
                "Compare At Price / International": "",
                "Status": "active"
            }
            writer.writerow(shopify_product)
    print(f"Export terminé : {csv_filename}")


# check products_shopify file entries count
# product_csv_filename = "products_shopify.csv"
# input_dir = "result/pro-elevage"
# product_file_path = os.path.join(input_dir, product_csv_filename)
# with open(product_file_path, mode='r', newline='', encoding='utf-8') as product_file:
#     reader = csv.DictReader(product_file)
#     for row in reader:
#         products.append(row)
#     print("End Reconstitution des Produits")
#     print(len(products))