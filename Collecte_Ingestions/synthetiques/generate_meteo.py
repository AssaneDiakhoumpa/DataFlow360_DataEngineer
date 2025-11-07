import os
from dotenv import load_dotenv
import random
from faker import Faker
import mysql.connector
from datetime import date

# Charger les variables d'environnement
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3307))
MYSQL_USER = os.getenv("MYSQL_USER", "meteo_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "meteo_pass")
MYSQL_DB = os.getenv("MYSQL_DB", "meteo_db")

faker = Faker('fr_FR')

# Liste Afrique de l’Ouest (un aéroport par pays)
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

# Connexion MySQL
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = conn.cursor()

# Création de la table
cursor.execute("""
CREATE TABLE IF NOT EXISTS donnees_meteo (
    id_meteo INT AUTO_INCREMENT PRIMARY KEY,
    pays VARCHAR(100),
    aeroport VARCHAR(150),
    date_observation DATE,
    heure_observation INT,
    temperature FLOAT,
    humidite FLOAT,
    pression FLOAT,
    vitesse_vent FLOAT,
    direction_vent VARCHAR(50),
    precipitations FLOAT,
    nebulosite FLOAT,
    visibilite FLOAT,
    point_rosee FLOAT,
    conditions_meteo VARCHAR(50)
);
""")
print("✅ Table donnees_meteo créée avec succès.")

# Insertion de données factices
N = 500
for _ in range(N):
    pays, aeroport = random.choice(AEROPORTS)
    cursor.execute("""
        INSERT INTO donnees_meteo (
            pays, aeroport, date_observation, heure_observation,
            temperature, humidite, pression, vitesse_vent, direction_vent,
            precipitations, nebulosite, visibilite, point_rosee, conditions_meteo
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        pays,
        aeroport,
        faker.date_between(start_date="-6mois", end_date="today"),
        random.randint(0, 23),
        random.uniform(15, 40),
        random.uniform(30, 100),
        random.uniform(980, 1030),
        random.uniform(0, 60),
        random.choice(["Nord", "Sud", "Est", "Ouest", "Sud-Ouest"]),
        random.uniform(0, 10),
        random.uniform(0, 100),
        random.uniform(1, 10),
        random.uniform(10, 25),
        random.choice(["Clair", "Pluie", "Orage", "Brouillard"])
    ))

conn.commit()
print(f"✅ {N} lignes météo insérées avec succès !")

cursor.close()
conn.close()
