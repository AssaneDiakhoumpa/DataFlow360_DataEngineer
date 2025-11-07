import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import redis
import json

# ===========================
# Connexion à Redis
# ===========================
r = redis.Redis(host='localhost', port=6379, db=0)
print("Connecté à Redis !")

# ===========================
# Mapping des codes compagnies
# ===========================
AIRLINE_CODES = {
    "SN": "Air Senegal", "SZN": "Air Senegal", "HC": "Air Senegal Express", "KP": "ASKY Airlines",
    "ET": "Ethiopian Airlines", "KQ": "Kenya Airways", "AT": "Royal Air Maroc", "MS": "EgyptAir",
    "SA": "South African Airways", "TC": "Air Tanzania", "AH": "Air Algérie", "TU": "Tunis Air",
    "L6": "Mauritania Airlines", "BJ": "Nouvelair", "FN": "Regional Air Services",
    "GF": "Gulf Air Bahrain", "J": "Air Burkina", "VU": "Air Ivoire", "VRE": "Virgin Nigeria",
    "APK": "APG Airlines", "OP": "Africa World Airlines", "AW": "Africa World Airlines",
    "GHN": "Ghana International Airlines", "Q": "Afrique Airlines", "RL": "Royal Falcon",
    "EK": "Emirates", "QR": "Qatar Airways", "EY": "Etihad Airways", "SV": "Saudi Arabian Airlines",
    "RJ": "Royal Jordanian", "ME": "Middle East Airlines", "WY": "Oman Air", "KU": "Kuwait Airways",
    "AF": "Air France", "KL": "KLM", "LH": "Lufthansa", "BA": "British Airways", "IB": "Iberia",
    "AZ": "ITA Airways", "TP": "TAP Air Portugal", "UX": "Air Europa", "LX": "Swiss",
    "OS": "Austrian Airlines", "SK": "SAS Scandinavian Airlines", "TK": "Turkish Airlines",
    "PC": "Pegasus Airlines", "DL": "Delta Air Lines", "UA": "United Airlines",
    "AA": "American Airlines", "FR": "Ryanair", "U": "easyJet", "VY": "Vueling",
    "TO": "Transavia", "W": "Wizz Air",
}

# ===========================
# Liste des aéroports à scrapper
# ===========================
airports = {
    "Sénégal": "DSS",
    "Ghana": "ACC",
    "Nigéria": "LOS",
    "Mali": "BKO",
    "Burkina Faso": "OUA",
    "Guinée": "CKY",
    "Togo": "LFW",
    "Côte d'Ivoire": "ABJ",
}

# ===========================
# Configuration Selenium
# ===========================
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# ===========================
# Boucle sur les aéroports
# ===========================
for country, airport in airports.items():
    print(f"\n Scraping de {airport} ({country})...")
    driver.get(f"https://www.flightstats.com/v2/flight-tracker/departures/{airport}")

    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table__TableRow-sc-1x7nv9w-7"))
        )
        time.sleep(5)

        rows = driver.find_elements(By.CLASS_NAME, "table__TableRow-sc-1x7nv9w-7")
        data = []

        for row in rows[1:]:
            cells = row.find_elements(By.CLASS_NAME, "table__Cell-sc-1x7nv9w-13")
            if len(cells) >= 4:
                vol_complet = cells[0].text.strip()
                code_compagnie = ''.join([c for c in vol_complet.split()[0] if c.isalpha()])
                compagnie = AIRLINE_CODES.get(code_compagnie, f"Inconnue ({code_compagnie})")

                vol_info = {
                    "Vol": vol_complet,
                    "Code_Compagnie": code_compagnie,
                    "Compagnie": compagnie,
                    "Heure_Depart": cells[1].text,
                    "Heure_Arrivee": cells[2].text,
                    "Destination": cells[3].text,
                    "Pays": country,
                    "Aeroport": airport
                }
                data.append(vol_info)

        df = pd.DataFrame(data)

        # Sauvegarde dans Redis
        if not df.empty:
            key = f"departures:{airport}"
            r.set(key, df.to_json(orient="records", force_ascii=False))
            print(f" {len(df)} vols enregistrés dans Redis sous la clé '{key}'")
        else:
            print(f" Aucun vol trouvé pour {airport}")

    except Exception as e:
        print(f" Erreur pour {airport}: {e}")

driver.quit()
print("\n Scraping terminé et données stockées dans Redis !")
