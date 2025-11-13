import requests
import boto3
import json
import time
from dotenv import load_dotenv
import os

# =============================
# Chargement des variables d'environnement
# =============================
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("API_KEY_OPENWEATHER")
REGION = "us-east-1"  # nécessaire pour Kinesis
KINESIS_STREAM = "dataflow"

# =============================
# Liste des aéroports d’Afrique de l’Ouest
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
# Configuration du client Kinesis (LocalStack)
# =============================
kinesis = boto3.client(
    "kinesis",
    region_name=REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    endpoint_url="http://localhost:4566"
)

# =============================
# Fonction de récupération météo
# =============================
def fetch_air_quality(lat, lon):
    """Récupère les données de qualité de l'air à partir des coordonnées"""
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    return response.json()

# =============================
# Envoi vers Kinesis
# =============================
def send_to_kinesis(payload):
    """Envoie les données JSON vers le flux Kinesis"""
    response = kinesis.put_record(
        StreamName=KINESIS_STREAM,
        Data=json.dumps(payload),
        PartitionKey=payload["ville"]
    )
    print(f"Données envoyées pour {payload['ville']} ({payload['pays']}) → Seq: {response['SequenceNumber']}")

# =============================
# Programme principal
# =============================
if __name__ == "__main__":
    for aeroport in aeroports:
        air_data = fetch_air_quality(aeroport["lat"], aeroport["lon"])
        record = {
            "pays": aeroport["pays"],
            "ville": aeroport["ville"],
            "aeroport": aeroport["nom"],
            "data": air_data,
            "timestamp": int(time.time())
        }
        send_to_kinesis(record)
        time.sleep(2)  # petite pause entre chaque envoi
