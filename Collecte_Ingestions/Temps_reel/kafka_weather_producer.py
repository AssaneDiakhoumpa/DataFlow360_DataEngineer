import json
import time
import requests
from kafka import KafkaProducer
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

# =============================
# Chargement des variables d'environnement
# =============================
load_dotenv()

API_KEY = os.getenv("API_KEY_OPENWEATHER")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "meteo_aeroports")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# =============================
# Liste des aéroports (nom, pays, lat, lon)
# =============================
aeroports = [
    {"pays": "Benin", "ville": "Cotonou", "nom": "Aéroport Cardinal Bernardin Gantin", "lat": 6.357, "lon": 2.384},
    {"pays": "Burkina Faso", "ville": "Ouagadougou", "nom": "Aéroport Thomas Sankara", "lat": 12.353, "lon": -1.512},
    {"pays": "Cap-Vert", "ville": "Praia", "nom": "Aéroport Nelson Mandela", "lat": 14.924, "lon": -23.493},
    {"pays": "Gambie", "ville": "Banjul", "nom": "Aéroport de Banjul", "lat": 13.338, "lon": -16.652},
    {"pays": "Ghana", "ville": "Accra", "nom": "Aéroport Kotoka", "lat": 5.603, "lon": -0.167},
    {"pays": "Guinée", "ville": "Conakry", "nom": "Aéroport Ahmed Sékou Touré", "lat": 9.576, "lon": -13.612},
    {"pays": "Guinée-Bissau", "ville": "Bissau", "nom": "Aéroport Osvaldo Vieira", "lat": 11.894, "lon": -15.653},
    {"pays": "Libéria", "ville": "Monrovia", "nom": "Aéroport Roberts", "lat": 6.239, "lon": -10.358},
    {"pays": "Mali", "ville": "Bamako", "nom": "Aéroport Modibo Keïta", "lat": 12.533, "lon": -7.95},
    {"pays": "Mauritanie", "ville": "Nouakchott", "nom": "Aéroport Nouakchott-Oumtounsy", "lat": 18.097, "lon": -15.947},
    {"pays": "Niger", "ville": "Niamey", "nom": "Aéroport Diori Hamani", "lat": 13.483, "lon": 2.183},
    {"pays": "Nigéria", "ville": "Lagos", "nom": "Aéroport Murtala Muhammed", "lat": 6.577, "lon": 3.321},
    {"pays": "Sénégal", "ville": "Dakar", "nom": "Aéroport Blaise Diagne", "lat": 14.67, "lon": -17.07},
    {"pays": "Sierra Leone", "ville": "Freetown", "nom": "Aéroport de Lungi", "lat": 8.616, "lon": -13.195},
    {"pays": "Togo", "ville": "Lomé", "nom": "Aéroport Gnassingbé Eyadéma", "lat": 6.166, "lon": 1.254}
]

# =============================
# Initialisation du Producer Kafka
# =============================
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Kafka Producer météo démarré...")

# =============================
# Boucle d’envoi des données
# =============================
while True:
    for aeroport in aeroports:
        try:
            params = {
                "lat": aeroport["lat"],
                "lon": aeroport["lon"],
                "appid": API_KEY,
                "units": "metric",
                "lang": "fr"
            }

            response = requests.get(BASE_URL, params=params)
            data = response.json()

            # Vérifie que la réponse API contient les données attendues
            if response.status_code != 200 or "main" not in data:
                print(f"Erreur API pour {aeroport['ville']} : {data}")
                continue

            meteo = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pays": aeroport["pays"],
                "ville": aeroport["ville"],
                "aeroport": aeroport["nom"],
                "temperature": data["main"]["temp"],
                "humidite": data["main"]["humidity"],
                "pression": data["main"]["pressure"],
                "vitesse_vent": data["wind"]["speed"],
                "direction_vent": data["wind"].get("deg", None),
                "conditions": data["weather"][0]["description"],
                "nuages": data["clouds"]["all"]
            }

            producer.send(TOPIC_NAME, meteo)
            print(f"Données envoyées pour {aeroport['ville']} : {meteo}")

        except Exception as e:
            print(f"Erreur pour {aeroport['ville']}: {e}")

        time.sleep(2)

    time.sleep(60)
