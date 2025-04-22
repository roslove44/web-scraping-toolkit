import os
import csv
from bs4 import BeautifulSoup
import requests
import re
import math


site_url = "https://www.loukko.com"
main_categories = [ 
    {"id": 1, "category": "Moottorikelkan lisävaruste Ale", "parent_id": None, "link": "https://www.loukko.com/ale/moottorikelkan-lisavaruste-ale"},
    {"id": 2, "category": "Moottorikelkkailu", "parent_id": None, "link": "https://www.loukko.com/moottorikelkkailu"},
    {"id": 3, "category": "Mönkijät", "parent_id": None, "link": "https://www.loukko.com/monkijat"},
    {"id": 4, "category": "Veneet ja vesijetit", "parent_id": None, "link": "https://www.loukko.com/veneet-ja-vesijetit"},
    {"id": 5, "category": "Piha & Metsä", "parent_id": None, "link": "https://www.loukko.com/metsa-ja-puutarha"},
    {"id": 6, "category": "Moottoripyöräily", "parent_id": None, "link": "https://www.loukko.com/moottoripyoraily"},
    {"id": 7, "category": "Koti & Autotalli", "parent_id": None, "link": "https://www.loukko.com/autotalli"},
    {"id": 8, "category": "Vaatteet & Varusteet", "parent_id": None, "link": "https://www.loukko.com/vaatteet-ja-ajovarusteet"},
    {"id": 9, "category": "Sähköpyörät", "parent_id": None, "link": "https://www.loukko.com/sahkopyorat"},
]
categories = []
visited_links = set()
current_id = 10

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

def get_categories_recursively(url, categories, parent_id):
    global current_id

    if url in visited_links:
        return
    visited_links.add(url)

    soup = extract_soup(url)
    if not soup:
        return

    parent_title = get_title(soup)
    
    ul_category = soup.find('ul', id='sidebar-menu')
    if not ul_category:
        print(f"⚠️ Aucune liste de catégories trouvée sur {parent_title}")
        return

    li_category = ul_category.find_all('li', attrs={'data-linkingmode': True})

    for li in li_category:
        a_tag = li.find('a')
        if a_tag and 'href' in a_tag.attrs:
            link = site_url + a_tag['href']
            title = a_tag.get_text(strip=True)

            # Ajouter la catégorie
            categories.append({"id": current_id, "category": title, "parent_id": parent_id, "link": link})
            new_parent_id = current_id
            current_id += 1

            get_categories_recursively(link, categories, new_parent_id)

def set_categories_file(main_categories, categories):
    for category in main_categories:
        print(f"🙄 Start {category['category']} ...")
        get_categories_recursively(category['link'], categories, category['id'])
        print(f"😩 End {category['category']}")
    
    csv_filename = "categories_all.csv"

    output_dir = "result/looko"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, csv_filename), mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "category", "parent_id", "link"])
        writer.writeheader()
        writer.writerows(main_categories)
        writer.writerows(categories)
    print(f"Export terminé : {csv_filename}")

def create_leaf_categories_file():
    input_dir = "result/looko"
    input_filename = "categories_all.csv"
    output_filename = "categories_leaf.csv"

    input_path = os.path.join(input_dir, input_filename)
    output_path = os.path.join(input_dir, output_filename)

    categories = []

    # Lire les catégories existantes
    with open(input_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            categories.append(row)

    print("📥 Lecture des catégories terminée.")

    # Identifier tous les IDs qui sont des parents
    parent_ids = set(row["parent_id"] for row in categories if row["parent_id"])

    # Sélectionner les catégories qui ne sont pas des parents (feuilles)
    leafs = [cat for cat in categories if cat["id"] not in parent_ids]

    print(f"🌿 {len(leafs)} catégories feuilles avant filtrage des doublons de lien.")

    # Supprimer les doublons basés sur le lien (link)
    unique_links = set()
    unique_leafs = []
    for leaf in leafs:
        if leaf["link"] not in unique_links:
            unique_leafs.append(leaf)
            unique_links.add(leaf["link"])

    print(f"✅ {len(unique_leafs)} catégories feuilles uniques après filtrage.")

    # Écriture des feuilles uniques dans un nouveau fichier
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["id", "category", "parent_id", "link"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_leafs)

    print(f"📁 Fichier généré : {output_filename}")

def get_one_page_products(page_url, category_id):
    global product_id
    print(f"📂 Scraping en cours : {page_url}")
    current_soup = extract_soup(page_url)
    if not current_soup:
        print(f"❌ Erreur : impossible de récupérer la page {page_url}")
        return
    
    products_container = current_soup.find_all('a', class_='product-list-item-link')
    if not products_container:
        print(f"Aucun produit trouvé sur la page : {page_url}")
        return
    for product in products_container:
        # Image du produit
        product_image_tag = product.find('div', class_='product-image').find('picture')
        product_image = site_url + product_image_tag.find('img').get('data-src') if product_image_tag and product_image_tag.find('img') else None

        # Lien du produit
        product_link = site_url + product.get('href')

        # Nom du produit
        product_title_tag = product.find('div', class_='product-title')
        product_title = product_title_tag.get_text(strip=True) if product_title_tag else "N/A"

        # Prix du produit
        product_price_tag = product.find('span', class_='price')
        if product_price_tag:
            raw_price = product_price_tag.get_text(strip=True)
            # Supprimer tout avant le premier chiffre
            product_price = re.sub(r'^[^\d]*', '', raw_price)
        else:
            product_price = "N/A"

        # Code du produit
        product_code_tag = product.find('div', class_='product-code')
        product_code = product_code_tag.get_text(strip=True) if product_code_tag else "N/A"

        products.append({"id": product_id, "name": product_title, "price": product_price, "image_src": product_image, "category_id": category_id, "link": product_link, "code": product_code})
        product_id += 1

def get_products(category):
    url = category['link']
    soup = extract_soup(url)
    if not soup:
        print(f"❌ Erreur : impossible de récupérer la page {url}")
        return

    total_pages = 1
    total_pages_container = soup.find('div', class_='total-pages')

    if total_pages_container:
        last_page_span = total_pages_container.find('span', class_='last-page-number')
        if last_page_span:
            try:
                total_pages = int(last_page_span.get_text(strip=True))
            except ValueError:
                total_pages = 1

    total_products_soup = soup.find('div', class_='product-count')
    if not total_products_soup:
        print(f"⚠️ Impossible de trouver le nombre total de produits sur {url}")
        return

    total_products_text = total_products_soup.get_text(strip=True) if total_products_soup else ""
    match = re.search(r'\d+', total_products_text)
    total_products = int(match.group()) if match else 0

    if total_products == 0:
        print(f"⚠️ Aucun produit trouvé sur {url}")
        return

    print(f"📊 {total_products} produits trouvés sur {total_pages} pages.")
    if total_pages >= 1:
        for page in range(1, total_pages + 1):
            page_url = f'{url}?page={page}'
            get_one_page_products(page_url, category['id'])

def set_products_file():
    csv_filename = "categories_leaf.csv"
    input_dir = "result/looko"
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
    output_dir = "result/looko"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, csv_filename), mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name", "price", "image_src", "category_id", "link", "code"])
        writer.writeheader()
        writer.writerows(products)
    print(f"Export terminé : {csv_filename}")

def set_products_file_by_main_category(main_categories):
    input_dir = "result/looko"
    categories_file = os.path.join(input_dir, "categories_all.csv")
    products_file = os.path.join(input_dir, "products_all.csv")
    output_dir = os.path.join(input_dir, "products_by_main_category")

    os.makedirs(output_dir, exist_ok=True)

    # Charger toutes les catégories du fichier
    with open(categories_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        all_categories = list(reader)

    # Construire un dictionnaire des enfants par parent_id
    children_map = {}
    for cat in all_categories:
        if(cat["parent_id"]):
            parent = int(cat["parent_id"])
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(int(cat["id"]))

    # Fonction pour récupérer récursivement tous les enfants d’un parent
    def get_descendants(parent_id):
        descendants = []
        direct_children = children_map.get(parent_id, [])
        for child_id in direct_children:
            descendants.append(child_id)
            descendants.extend(get_descendants(child_id))  # récursion
        return descendants

    # Construction du mapping final
    main_category_tree = {}
    for main_cat in main_categories:
        main_id = int(main_cat["id"])
        all_sub_ids = get_descendants(main_id)
        main_category_tree[main_id] = all_sub_ids
        print(f"{main_cat['category']} ➜ {len(all_sub_ids)} sous-catégories trouvées")
    # return main_category_tree

    # Charger les produits
    with open(products_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        all_products = list(reader)
        product_headers = reader.fieldnames

    # Boucler sur chaque main category via son ID
    for main_id, descendants in main_category_tree.items():
        # On prend les produits dont category_id est dans descendants
        filtered_products = [
            product for product in all_products
            if product.get("category_id") and int(product["category_id"]) in descendants
        ]

        # Définir le nom du fichier (ex: 1.csv, 2.csv...)
        output_file = os.path.join(output_dir, f"{main_id}.csv")

        # Écrire dans le fichier
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=product_headers)
            writer.writeheader()
            writer.writerows(filtered_products)

        print(f"[✓] Fichier '{main_id}.csv' créé avec {len(filtered_products)} produits.")

def get_product_description(page_url):
    current_soup = extract_soup(page_url)
    product_description= ''
    if(current_soup):
        product_description = current_soup.select_one('#Kuvaus')

    return {
        "product_description": product_description if product_description else '',
    }

def set_products_to_shopify_file(number):
    input_dir = "result/looko"
    categories_file = os.path.join(input_dir, "categories_all.csv")
    products_file = os.path.join(input_dir+'/products_by_main_category', f"{number}.csv")
    output_dir = os.path.join(input_dir, "products_by_main_category")

    os.makedirs(output_dir, exist_ok=True)

    # Charger toutes les catégories du fichier
    with open(categories_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        all_categories = list(reader)
    
    # Charger les produits
    with open(products_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        all_products = list(reader)
    
    # Définir le nom du fichier
    output_file = os.path.join(output_dir, f"{number}_shopify.csv")
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
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
            "Price / International", "Compare At Price / International", "Status", "Custom Product Type", "Collection"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        n=1
        for product in all_products:
            print(f"🙄 Start {product['name']} hunting... {n}/{len(all_products)}")
            descriptions = get_product_description(product['link'])
            shopify_product = {
                "Handle": product['name'],
                "Title": product['name'],
                "Body (HTML)": descriptions['product_description'],
                "Vendor": None,  
                "Product Category": None,
                "Type": None,
                "Tags": all_categories[int(product['category_id'])-1]['category'],
                "Custom Product Type": all_categories[int(product['category_id'])-1]['category'],
                "Published": "TRUE",
                "Option1 Name": "",
                "Option1 Value": "",
                "Variant SKU": product['code'],
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
                "Google Shopping / Google Product Category": all_categories[int(product['category_id'])-1]['category'],
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
                "Status": "active",
                "Collection" : main_categories[number-1]['category']
            }
            writer.writerow(shopify_product)
            n= n+1
    print(f"Export terminé : {output_file}")


# check products_shopify file entries count
def check_products_length_in_file(folder, file):
    the_dir = os.path.join(folder, file)
    with open(the_dir, mode='r', newline='', encoding='utf-8') as product_file:
        reader = csv.DictReader(product_file)
        for row in reader:
            products.append(row)
        print("End Reconstitution des Produits")
        print(len(products))

check_products_length_in_file("result/looko/products_by_main_category", "9_shopify.csv")

def contnue_set_products_to_shopify_file(number, start):
    input_dir = "result/looko"
    categories_file = os.path.join(input_dir, "categories_all.csv")
    products_file = os.path.join(input_dir+'/products_by_main_category', f"{number}.csv")
    output_dir = os.path.join(input_dir, "products_by_main_category")

    os.makedirs(output_dir, exist_ok=True)

    # Charger toutes les catégories du fichier
    with open(categories_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        all_categories = list(reader)
    
    # Charger les produits
    with open(products_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        all_products = list(reader)
        length = (len(all_products))
        all_products = all_products[start:length]
    
    # Définir le nom du fichier
    output_file = os.path.join(output_dir, f"{number}_shopify.csv")
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
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
            "Price / International", "Compare At Price / International", "Status", "Custom Product Type", "Collection"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        n=1
        for product in all_products:
            print(f"🙄 Start {product['name']} hunting... {n}/{len(all_products)}")
            descriptions = get_product_description(product['link'])
            shopify_product = {
                "Handle": product['name'],
                "Title": product['name'],
                "Body (HTML)": descriptions['product_description'],
                "Vendor": None,  
                "Product Category": None,
                "Type": None,
                "Tags": all_categories[int(product['category_id'])-1]['category'],
                "Custom Product Type": all_categories[int(product['category_id'])-1]['category'],
                "Published": "TRUE",
                "Option1 Name": "",
                "Option1 Value": "",
                "Variant SKU": product['code'],
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
                "Google Shopping / Google Product Category": all_categories[int(product['category_id'])-1]['category'],
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
                "Status": "active",
                "Collection" : main_categories[number-1]['category']
            }
            writer.writerow(shopify_product)
            n= n+1
    print(f"Export terminé : {output_file}")

