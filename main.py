import os
import csv
from bs4 import BeautifulSoup
import requests

categories = []
url_categories = [
    "https://www.vetementpro.com/4-artisanat-btp-industrie",
    "https://www.vetementpro.com/54-metiers-de-bouche",
    "https://www.vetementpro.com/22-tenues-sante"
]


def extract_url(url):
    # Cette fonction extrait le contenu HTML d'une URL donnée.
    # Elle envoie une requête à l'URL et récupère la réponse.
    response = requests.get(url)
    html_response = response.content
    return html_response


def get_title(soup):
    return soup.title.string


def get_categories(soup, categories):
    # Cette fonction extrait les catégories à partir d'un objet BeautifulSoup représentant une page HTML.
    # Elle recherche l'élément <ul> avec la classe CSS 'tree' et récupère la première occurrence.
    ul_category = ul_list = soup.find_all('ul', class_='tree')[0]

    # Ensuite, elle recherche tous les éléments <li> avec la classe CSS 'category-element' à l'intérieur de l'élément <ul>.
    li_category = ul_category.find_all('li', class_='category-element')

    # Pour chaque élément <li> trouvé, elle extrait l'attribut 'href' de la balise <a> et l'ajoute à la liste des catégories.
    for li in li_category:
        category = li.find('a')['href']
        categories.append(category)


def get_page_products_info(soup):
    # Cette fonction extrait le nombre de pages de produits disponibles sur une page donnée.
    # Elle recherche l'élément <ul> avec la classe CSS 'page-list' à l'aide de BeautifulSoup.
    ul_list = soup.find_all('ul', class_='page-list')

    if ul_list:
        # Si l'élément <ul> est trouvé, elle récupère tous les éléments <li> à l'intérieur.
        li_list = ul_list[0].find_all('li')

        # Le nombre de pages est généralement situé à l'avant-dernier élément de la liste <li>.
        # On extrait le texte, on le nettoie avec strip() et on le convertit en entier.
        last_page = li_list[-2].get_text().strip()
        return int(last_page)
    else:
        # Si l'élément <ul> n'est pas trouvé, cela signifie qu'il n'y a qu'une seule page de produits.
        return 1


def get_all_products_info(soup, products: list[dict]):
    # Cette fonction extrait les informations de tous les produits d'une page donnée.
    # Elle recherche tous les conteneurs de vignettes de produits à l'aide de BeautifulSoup.
    thumbnail_containers = soup.find_all('div', class_='thumbnail-container')
    for container in thumbnail_containers:
        # Pour chaque conteneur de vignette, on extrait le lien de l'image du produit.
        anchor = container.find('a', class_='thumbnail product-thumbnail')
        img_src = anchor.find('img')['src']

        # On extrait également le titre du produit en recherchant les éléments appropriés dans la description du produit.
        product_description = container.find(
            'div', class_='product-description')
        product_title = product_description.find(
            'h2', class_='product-title').find('a').get_text()

        # De plus, on extrait le prix du produit en recherchant les éléments appropriés dans la description du produit.
        product_price = product_description.find(
            'div', class_='product-price-and-shipping').find('span', class_='price').get_text()

        # On supprime les caractères indésirables (comme les espaces insécables) du prix et on le nettoie avec strip().
        product_price = product_price.replace('\xa0', '').strip()

        # On crée un dictionnaire pour stocker les informations du produit extrait.
        product = {
            'title': product_title,
            'price': product_price,
            'img_src': img_src
        }
        products.append(product)


def load_data(save_folders, soup, products):
    # Cette fonction charge les données extraites dans un fichier CSV.
    # Elle utilise le titre de la page pour générer le nom du fichier CSV.
    title = get_title(soup).strip().replace(
        "-", "_").replace("/", "_").replace(" ", "_").replace(":", "_").replace("|", "")

    # On ouvre le fichier CSV en mode écriture et on spécifie l'encodage.
    with open(f'{save_folders}/{title}.csv', mode='w', newline='', encoding='utf-8') as file:
        # On spécifie les noms des colonnes dans le fichier CSV.
        fieldnames = ['index', 'title', 'price', 'img_src']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # On écrit l'en-tête du fichier CSV avec les noms des colonnes.
        writer.writeheader()

        # On initialise un compteur d'index.
        index = 1

        # Pour chaque produit extrait, on ajoute un index, puis on écrit les données du produit dans une ligne du fichier CSV.
        for product in products:
            product['index'] = index
            writer.writerow(product)
            index += 1


def main():
    # Cette fonction est le point d'entrée principal du programme.
    # Elle itère sur chaque URL de catégorie dans la liste 'url_categories'.
    for each_url_categories in url_categories:
        # On extrait le contenu HTML de la page de catégorie.
        html_categories = extract_url(each_url_categories)
        soup_categories = BeautifulSoup(html_categories, 'html.parser')

        # On obtient le titre de la page de catégorie pour créer un nom de dossier.
        save_folders = get_title(soup_categories).strip().replace(
            "-", "_").replace("/", "_").replace(" ", "_").replace(":", "_").replace("|", "")
        if not os.path.exists(save_folders):
            os.makedirs(save_folders)

        # On obtient toutes les catégories présentes sur la page de catégorie.
        get_categories(soup_categories, categories)

        # Pour chaque catégorie, on extrait les produits.
        for category in categories:
            products = []
            html = extract_url(category)
            soup = BeautifulSoup(html, 'html.parser')

            # On détermine le nombre total de pages de produits dans la catégorie.
            last_page = get_page_products_info(soup) + 1
            x_page = 1
            while x_page < last_page:
                category_url = f"{category}?page={x_page}"
                x_page += 1
                html = extract_url(category_url)
                soup = BeautifulSoup(html, 'html.parser')
                get_all_products_info(soup, products)
            # On charge les données extraites dans un fichier CSV.
            load_data(save_folders, soup, products)
            print(
                '\033[92m' + f"\u2714 Création du fichier réussie pour la catégorie : {category}" + '\033[0m')


if __name__ == "__main__":
    main()
