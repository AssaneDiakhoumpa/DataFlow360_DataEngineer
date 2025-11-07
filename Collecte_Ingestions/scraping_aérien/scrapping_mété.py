import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import redis
import json

# ===============================
# Connexion à Redis
# ===============================
r = redis.Redis(host="localhost", port=6379, db=0)
print(" Connecté à Redis !")

# ===============================
# Liste des aéroports / villes
# ===============================
airports = {
    "Sénégal - Dakar": "Dakar",
    "Ghana - Accra": "Accra",
    "Nigéria - Lagos": "Lagos",
    "Mali - Bamako": "Bamako",
    "Burkina Faso - Ouagadougou": "Ouagadougou",
    "Guinée - Conakry": "Conakry",
    "Togo - Lomé": "Lome",
    "Côte d'Ivoire - Abidjan": "Abidjan",
    "Bénin - Cotonou": "Cotonou",
    "Niger - Niamey": "Niamey",
    "Mauritanie - Nouakchott": "Nouakchott",
    "Gambie - Banjul": "Banjul",
    "Guinée-Bissau - Bissau": "Bissau",
    "Liberia - Monrovia": "Monrovia",
    "Sierra Leone - Freetown": "Freetown",
    "Cap-Vert - Praia": "Praia",
}

# Colonnes météo (tu gardes ta structure)
colonnes = [
    "date", "timestamp", "temp_max", "temp_min", "temp_moy", "real_feel_max", "real_feel_min",
    "real_feel_moy", "humidity_max", "humidity_min", "humidity_moy", "wind_speed",
    "precipitation_mm", "precipitation_hours", "snow_mm", "snow_hours", "precip_type",
    "rain_mm", "snow_depth", "wind_gust", "wind_direction_deg", "wind_direction_cardinal",
    "visibility_km", "uv_index", "sunrise", "sunset", "moon_phase", "conditions_text",
    "conditions_icon", "temp_sol_max", "temp_sol_min", "temp_sol_moy", "indice_uv",
    "dew_point", "storm", "station"
]

first_run = True

# ===============================
#  Boucle principale
# ===============================
for location_name, city in airports.items():
    print(f"\n{'='*60}")
    print(f" Scraping météo pour {location_name}...")
    print(f"{'='*60}")
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.visualcrossing.com/weather-query-builder/")
        
        # Gestion des popups (cookies, welcome)
        if first_run:
            try:
                accept_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept all cookies')]"))
                )
                accept_btn.click()
                print(" Popup cookies accepté.")
                time.sleep(2)
            except Exception:
                print("Pas de popup cookies détecté.")
            
            try:
                close_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]"))
                )
                close_btn.click()
                print(" Popup bienvenue fermé.")
                time.sleep(2)
            except Exception:
                print("Pas de popup bienvenue détecté.")
            
            first_run = False
        
        # Saisie de la ville
        search_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter a location']"))
        )
        search_input.clear()
        time.sleep(1)
        search_input.send_keys(city)
        search_input.send_keys(Keys.ENTER)
        print(f" Recherche lancée pour {city}...")
        
        # Attente du chargement
        time.sleep(10)
        
        tables = driver.find_elements(By.TAG_NAME, "table")
        data = []
        
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    row_data.append(location_name)
                    data.append(row_data)
        
        if data:
            df_temp = pd.DataFrame(data)
            
            # Adapter les colonnes
            if len(df_temp.columns) <= len(colonnes):
                df_temp.columns = colonnes[:len(df_temp.columns)]
            else:
                df_temp.columns = colonnes + [f"col_{i}" for i in range(len(df_temp.columns) - len(colonnes))]
            
            print(f" {len(df_temp)} lignes extraites pour {location_name}")
            print(df_temp.head())

            # Envoi vers Redis
            key = f"meteo:{city.lower()}"
            r.set(key, df_temp.to_json(orient="records", force_ascii=False))
            print(f" Données météo enregistrées dans Redis sous la clé '{key}'")

        else:
            print(f" Aucune donnée trouvée pour {city}")
    
    except Exception as e:
        print(f" Erreur pour {location_name}: {e}")
    
    finally:
        try:
            driver.quit()
        except:
            pass
    
    time.sleep(3)

print("\n Scraping météo terminé et stocké dans Redis !")
