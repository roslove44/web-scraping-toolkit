# web-scraping-toolkit

Un ensemble d'outils de web scraping pour extraire et analyser des données à partir de sites web spécifiques.

# Documentation du Projet de Web Scraping

Ce document fournit une documentation détaillée pour le projet de web scraping réalisé. Il explique le fonctionnement du projet, les dépendances requises, les étapes d'installation, et fournit des exemples d'utilisation.

## But du Projet

Le but de ce projet est de présenter une démonstration pratique du web scraping, qui est une technique d'extraction et d'analyse de données à partir de sites web. Dans cet exemple, nous avons choisi un site e-commerce comme cas d'utilisation.

#https://www.vetementpro.com/

Le projet vise à illustrer les étapes nécessaires pour récupérer des données à partir d'un site web spécifique et les enregistrer dans un format structuré, tel qu'un fichier CSV. Il démontre également l'utilisation d'outils populaires tels que Python, les bibliothèques BeautifulSoup et Requests, ainsi que les concepts de base du HTML.

Il est important de noter que ce projet est basé sur la structure spécifique du site web choisi comme exemple. Ainsi, pour adapter le code à d'autres sites web, des modifications seront nécessaires en fonction de la structure de chaque site.

Ce projet s'adresse aux personnes intéressées par le web scraping, souhaitant comprendre les concepts fondamentaux et apprendre comment extraire des données à partir de sites web. Des connaissances de base en HTML sont recommandées pour une meilleure compréhension du code et de la structure du site.

N'hésitez pas à explorer le code source, à l'utiliser comme point de départ pour vos propres projets et à l'adapter en fonction de vos besoins spécifiques.

Nous espérons que cette démonstration vous sera utile dans votre apprentissage du web scraping et vous inspirera pour vos futurs projets !

## Fonctionnalités

Le projet de web scraping permet d'extraire et d'analyser des données à partir de sites web spécifiques. Il offre les fonctionnalités suivantes :

- Extraction de données : Le projet utilise la bibliothèque BeautifulSoup pour extraire les données HTML des pages web ciblées.
- Analyse des données : Les données extraites sont analysées pour extraire des informations spécifiques telles que les titres, les prix et les images des produits.
- Enregistrement des données : Les données extraites sont enregistrées dans des fichiers CSV pour une utilisation ultérieure.

## Dépendances

Le projet de web scraping utilise les dépendances suivantes :

- Python (version 3.x) : Langage de programmation utilisé pour le développement du projet.
- Requests : Bibliothèque Python pour envoyer des requêtes HTTP et récupérer les réponses.
- BeautifulSoup : Bibliothèque Python pour analyser des documents HTML et extraire les données.
- CSV : Module Python pour lire et écrire des fichiers CSV.
- OS : Module Python pour effectuer des opérations sur le système d'exploitation, telles que la création de dossiers.

## Installation

Pour exécuter le projet de web scraping, suivez les étapes ci-dessous :

1. Assurez-vous d'avoir Python installé sur votre machine. Vous pouvez le télécharger à partir du site officiel de Python (https://www.python.org).

2. Clonez le dépôt GitHub du projet sur votre machine en utilisant la commande suivante :

   ```
   git clone [URL du dépôt GitHub]
   ```

3. Accédez au répertoire du projet en utilisant la commande `cd` (change directory) :

   ```
   cd nom_du_projet
   ```

4. Installez les dépendances requises en exécutant la commande suivante :

   ```
   pip install -r requirements.txt
   ```

5. Une fois les dépendances installées, vous pouvez exécuter le projet en utilisant la commande suivante :

   ```
   python main.py
   ```

## Utilisation

Pour utiliser le projet de web scraping, suivez les étapes ci-dessous :

1. Modifiez la liste `url_categories` dans le fichier `main.py` en ajoutant les URL des catégories que vous souhaitez scraper.
2. Exécutez le fichier `main.py` en utilisant la commande `python main.py`. Le projet commencera à scraper les données des sites web spécifiés.

3. Les données extraites seront enregistrées dans des fichiers CSV, un fichier par catégorie.
![pyton data extraction result](https://github.com/roslove44/web-scraping-toolkit/assets/90060938/6f3603c3-969c-4ee4-b6b5-984a3b1ab6f7)



## Exemples

Voici un exemple d'utilisation du projet de web scraping :

```python
# Import des modules requis
import requests
from bs4 import BeautifulSoup

# URL à scraper
url = "https://www.example.com"

# Envoi de la requête HTTP
response = requests.get(url)

# Extraction des données HTML
html = response.content

# Création de l'objet BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Extraction des informations spécifiques
title = soup.title.string


product = soup.find('div', class_='product')
product_name = product.find('h2').text
product_price = product.find('span', class_='price').text

# Affichage des résultats
print("Titre de la page:", title)
print("Nom du produit:", product_name)
print("Prix du produit:", product_price)
```

Ce code montre comment envoyer une requête HTTP à une URL spécifique, extraire les données HTML à l'aide de BeautifulSoup, et extraire des informations spécifiques de la page web.

## Contribuer

Si vous souhaitez contribuer à l'amélioration du projet de web scraping, vous pouvez suivre les étapes suivantes :

1. Forker le dépôt GitHub du projet.
2. Créer une nouvelle branche pour vos modifications.
3. Effectuer les modifications souhaitées et les tester.
4. Soumettre une demande de pull (pull request) avec une description détaillée de vos modifications.

Nous apprécions toutes les contributions et les suggestions d'amélioration du projet !

## Liens utiles

1. Documentation BeautifulSoup : https://www.crummy.com/software/BeautifulSoup/bs4/doc/
2. Documentation Requests : https://requests.readthedocs.io/en/latest/
3. Documentation Csv : https://docs.python.org/3/library/csv.html
4. Documentation Os : https://docs.python.org/3/library/os.html

## Licence

Ce projet est distribué sous la licence MIT. Vous pouvez consulter le fichier `LICENSE` pour plus d'informations sur les conditions de la licence.

---
