from kafka import KafkaProducer
import requests
import json
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
import time
import os
from dotenv import load_dotenv

load_dotenv()
# Variables d'environnement
API_KEY = os.getenv("AVIATIONSTACK_KEY")
KAFKA_SERVERS = os.getenv("KAFKA_SERVERS", "localhost:9092")
TOPIC_NAME_FLIGHTS = os.getenv("TOPIC_NAME_FLIGHTS", "vols_ao")

# Kafka Producer config
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVERS],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks='all',
    retries=3
)

# Liste des aéroports principaux
airports = {
    "Bénin": ["COO"],
    "Burkina Faso": ["OUA"],
    "Cap-Vert": ["RAI"],
    "Gambie": ["BJL"],
    "Ghana": ["ACC"],
    "Guinée": ["CKY"],
    "Guinée-Bissau": ["OXB"],
    "Libéria": ["ROB"],
    "Mali": ["BKO"],
    "Mauritanie": ["NKC"],
    "Niger": ["NIM"],
    "Nigéria": ["LOS"],
    "Sénégal": ["DSS"],
    "Sierra Leone": ["FNA"],
    "Togo": ["LFW"]
}

# Fonctions utilitaires
def get_country_from_iata(iata_code):
    for country, codes in airports.items():
        if iata_code in codes:
            return country
    return "Inconnu"

def get_flights(iata_code):
    """Récupère les 5 premiers vols d’un aéroport donné."""
    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Erreur API {iata_code}: {response.status_code}")
            return []

        data = response.json()
        flights = []
        for flight in data.get("data", [])[:5]:
            flights.append({
                "compagnie": flight["airline"]["name"] if flight.get("airline") else None,
                "numero_vol": flight["flight"]["iata"] if flight.get("flight") else None,
                "aeroport_depart": flight["departure"]["airport"] if flight.get("departure") else None,
                "aeroport_arrivee": flight["arrival"]["airport"] if flight.get("arrival") else None,
                "heure_depart_prevue": flight["departure"]["scheduled"] if flight.get("departure") else None,
                "etat_vol": flight.get("flight_status"),
                "pays": get_country_from_iata(iata_code),
                "timestamp": datetime.utcnow().isoformat()
            })
        return flights

    except Exception as e:
        print(f" Erreur récupération {iata_code} → {e}")
        return []

# Tâche principale à planifier
def run_producer():
    print(f"\n Lancement du producteur ({datetime.now()})\n")
    total = 0
    for country, codes in airports.items():
        for code in codes:
            flights = get_flights(code)
            for f in flights:
                producer.send(TOPIC_NAME_FLIGHTS, value=f)
                print(f" {f['pays']} - {f['numero_vol']} envoyé.")
                total += 1
            time.sleep(2)
    producer.flush()
    print(f"\n {total} vols envoyés à {datetime.now().strftime('%H:%M:%S')}.\n")

# Planification automatique
if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=pytz.timezone("Africa/Dakar"))

    # Tâches planifiées à 09h00 et 21h00
    scheduler.add_job(run_producer, 'cron', hour=11, minute=30)
    scheduler.add_job(run_producer, 'cron', hour=12, minute=0)

    print("Scheduler en attente des exécutions (11h30 & 12h00)...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler arrêté proprement.")
