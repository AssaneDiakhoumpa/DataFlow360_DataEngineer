#  Projet DataFlow360 – Collecte & Ingestion Multi-Source

##  Contexte du projet

**DataFlow360** est une plateforme de traitement et d’analyse de données aériennes et météorologiques.  
Cette première phase du projet met l’accent sur la **collecte et l’ingestion multi-source** des données, constituant la base de toute la chaîne data (ETL/ELT).

L’objectif principal est de construire une **pipeline de collecte robuste, conteneurisée et modulaire**, capable d’ingérer différentes sources de données :
- Données synthétiques (générées avec `Faker`)
- Données issues de fichiers plats (CSV)
- Données issues de **scraping web** avec `Selenium`
- Données temps réel provenant d’**APIs externes** (AviationStack, OpenWeather)
- Données temporaires et intermédiaires stockées dans plusieurs bases (Redis, MySQL, Cassandra)
- Données en streaming envoyées vers un **cluster Kafka**

---

## Architecture Technique

###  Vue d’ensemble

![Architecture de Collecte & Ingestion](assets/Collecte_injection.drawio.png)

Cette architecture illustre les différents canaux de collecte et leur intégration dans le pipeline Multi-Source.

###  Sources de données
| Source | Description | Technologie |
|--------|--------------|--------------|
| **FAKER** | Génération de données aériennes et météorologiques simulées | Python / Faker |
| **Fichiers CSV** | Données plats importées localement | Pandas / CSV |
| **Scraping** | Extraction de données web (vols, météo) | Selenium |
| **APIs** | Données temps réel (météo, trafic aérien) | OpenWeather, AviationStack |

###  Stockages intermédiaires
| Base | Rôle | Type |
|------|------|------|
| **Redis** | Cache et buffer des données brutes | NoSQL (Key-Value) |
| **MySQL** | Données structurées, persistantes | SQL (Relationnel) |
| **Cassandra** | Données volumineuses et distribuées | NoSQL (Colonne) |

### 🔹 Pipeline Kafka
- **Kafka Producer Python** : publie les messages en temps réel dans le cluster
- **Kafka Cluster** : reçoit les données sur plusieurs *topics* (aérien, météo)
- **Kafka Partitioning** : assure la scalabilité et la tolérance aux pannes

## Technologies utilisées

| Catégorie | Outils / Librairies |
|------------|---------------------|
| Langage principal | Python 3 |
| Conteneurisation | Docker & Docker Compose |
| Streaming | Apache Kafka |
| Bases de données | MySQL, Redis, Cassandra |
| APIs externes | OpenWeather, AviationStack |
| Génération de données | Faker |
| Web Scraping | Selenium |
| Gestion de dépendances | requirements.txt |
| Notebook d’analyse | Jupyter (optionnel) |


## Lancer le projet avec Docker

### Cloner le dépôt
```bash
git clone https://github.com/<AssaneDiakhoumpa>/DataFlow360.git
cd DataFlow360
````

### Construire et lancer les conteneurs

```bash
docker-compose up --build
```

### Vérifier les services

* Kafka Cluster : `localhost:9092`
* Redis : `localhost:6379`
* MySQL : `localhost:3306`
* Cassandra : `localhost:9042`


## Fonctionnement du pipeline

1. Les scripts `generate_*.py` génèrent des données simulées.
2. Les scrapers Selenium collectent des données réelles depuis le web.
3. Les API OpenWeather & AviationStack fournissent des données en temps réel.
4. Toutes ces données transitent par Redis / MySQL / Cassandra selon leur nature.
5. Les producteurs Kafka publient les messages dans le cluster Kafka.
6. Les topics Kafka peuvent ensuite être consommés pour les étapes suivantes :

   * Nettoyage
   * Transformation
   * Analyse / Machine Learning


## Sécurité & Environnement

* Les accès API sont définis dans le fichier `.env` (non partagé publiquement).
* Chaque conteneur communique via un réseau Docker interne.
* Les données sont simulées ou publiques : **aucune donnée sensible** n’est collectée.


## Prochaines étapes

**Étape 2 : Nettoyage & Transformation**

* Standardisation des schémas de données
* Vérification des types et valeurs manquantes
* Construction du Data Lake / Data Warehouse

**Étape 3 : Orchestration & Monitoring**

* Intégration d’Airflow pour planifier les pipelines
* Centralisation des logs et alertes (ELK / Prometheus)
