import os
from dotenv import load_dotenv
from faker import Faker
import random
import uuid
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# CHARGEMENT VARIABLES D'ENVIRONNEMENT
load_dotenv()

CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "localhost")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", 9042))
CASSANDRA_USERNAME = os.getenv("CASSANDRA_USERNAME", "cassandra")
CASSANDRA_PASSWORD = os.getenv("CASSANDRA_PASSWORD", "cassandra")
KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "aerien")
TABLE = "vols"

faker = Faker('fr_FR')

#  LISTE AFRIQUE DE L’OUEST
AEROPORTS = [
    ("Bénin", "Aéroport International Cardinal Bernardin Gantin (Cotonou)"),
    ("Burkina Faso", "Aéroport International Thomas Sankara (Ouagadougou)"),
    ("Cap-Vert", "Aéroport International Nelson Mandela (Praia)"),
    ("Gambie", "Aéroport International de Banjul"),
    ("Ghana", "Aéroport International Kotoka (Accra)"),
    ("Guinée", "Aéroport International Ahmed Sékou Touré (Conakry)"),
    ("Guinée-Bissau", "Aéroport International Osvaldo Vieira (Bissau)"),
    ("Libéria", "Aéroport International Roberts (Monrovia)"),
    ("Mali", "Aéroport International Modibo Keïta (Bamako)"),
    ("Mauritanie", "Aéroport International de Nouakchott-Oumtounsy"),
    ("Niger", "Aéroport International Diori Hamani (Niamey)"),
    ("Nigéria", "Aéroport International Murtala Muhammed (Lagos)"),
    ("Sénégal", "Aéroport International Blaise Diagne (Dakar)"),
    ("Sierra Leone", "Aéroport International de Lungi (Freetown)"),
    ("Togo", "Aéroport International Gnassingbé Eyadéma (Lomé)")
]

COMPAGNIES = [
    "Air Sénégal", "Air Burkina", "ASKY Airlines", "Air Côte d’Ivoire",
    "Air France", "Royal Air Maroc", "Turkish Airlines"
]

TYPES_AVION = ["A320", "A330", "B737", "B787", "E190"]

#  CONNEXION À CASSANDRA
auth_provider = PlainTextAuthProvider(username=CASSANDRA_USERNAME, password=CASSANDRA_PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect()

# Création du keyspace si non existant
session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 1 }};
""")

session.set_keyspace(KEYSPACE)

# Création de la table
session.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE} (
        id_vol UUID,
        numero_vol text,
        compagnie text,
        type_appareil text,
        aeroport_depart text,
        pays_depart text,
        destination text,
        distance_vol_km float,
        heure_depart int,
        jour_semaine text,
        mois text,
        saison text,
        retard_min float,
        retard int,
        date_vol date,
        PRIMARY KEY ((pays_depart, aeroport_depart), date_vol, id_vol)
    );
""")

print("Keyspace et table créés avec succès.")

# GÉNÉRATION DE DONNÉES
insert_query = session.prepare(f"""
    INSERT INTO {TABLE} (
        id_vol, numero_vol, compagnie, type_appareil,
        aeroport_depart, pays_depart, destination,
        distance_vol_km, heure_depart, jour_semaine, mois,
        saison, retard_min, retard, date_vol
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""")

N = 500  # nombre de vols à générer

for i in range(N):
    pays, aeroport = random.choice(AEROPORTS)
    retard_min = round(random.uniform(0, 60), 2)

    session.execute(insert_query, (
        uuid.uuid4(),
        faker.bothify(text='??###'),
        random.choice(COMPAGNIES),
        random.choice(TYPES_AVION),
        aeroport,
        pays,
        random.choice(["Paris", "Madrid", "Casablanca", "Lisbonne", "Abidjan", "Lomé"]),
        round(random.uniform(200, 5000), 2),
        random.randint(0, 23),
        faker.day_of_week(),
        faker.month_name(),
        random.choice(["Sèche", "Pluvieuse"]),
        retard_min,
        1 if retard_min > 15 else 0,
        faker.date_between(start_date="-6mois", end_date="today")
    ))

    if (i + 1) % 50 == 0:
        print(f"{i+1}/{N} vols générés...")

print("Génération terminée avec succès !")

cluster.shutdown()
