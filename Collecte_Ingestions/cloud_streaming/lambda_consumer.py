import json
import boto3
import base64
from datetime import datetime
from decimal import Decimal

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('dataflow_mongo')
    
    print(f"🔗 Connexion à DynamoDB")
    print(f"📦 Nombre d'enregistrements: {len(event['Records'])}")
    
    for i, record in enumerate(event['Records']):
        try:
            # Décodage base64 des données Kinesis
            payload_raw = base64.b64decode(record['kinesis']['data'])
            payload = json.loads(payload_raw)
            
            print(f"\n--- Record {i+1} ---")
            print(f"📥 Payload complet: {json.dumps(payload, indent=2)}")
            
            # Vérifier que les clés existent
            if 'ville' not in payload:
                raise ValueError("Clé 'ville' manquante dans le payload")
            if 'timestamp' not in payload:
                raise ValueError("Clé 'timestamp' manquante dans le payload")
            
            # Extraction des données avec conversion explicite
            ville = str(payload['ville'])
            pays = str(payload.get('pays', 'Inconnu'))
            aeroport = str(payload.get('aeroport', 'Inconnu'))
            air_data = payload.get('data', {})
            timestamp = int(payload['timestamp'])
            
            # Conversion du timestamp en date STRING
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"🔑 ville (type={type(ville)}): '{ville}'")
            print(f"🔑 date (type={type(date_str)}): '{date_str}'")
            
            # Préparer l'item
            item = {
                'ville': ville,
                'date': date_str,
                'pays': pays,
                'aeroport': aeroport,
                'air_quality': json.dumps(air_data),
                'timestamp': Decimal(str(timestamp))
            }
            
            print(f"💾 Item à insérer: {json.dumps(item, default=str)}")
            
            # Insertion dans DynamoDB
            response = table.put_item(Item=item)
            
            print(f"✅ Insertion réussie pour {ville} - {date_str}")
            print(f"📊 Réponse: {response.get('ResponseMetadata', {}).get('HTTPStatusCode', 'N/A')}")
            
        except Exception as e:
            print(f"\n❌ ERREUR pour le record {i+1}")
            print(f"Type d'erreur: {type(e).__name__}")
            print(f"Message: {str(e)}")
            print(f"Payload brut (base64): {record['kinesis']['data']}")
            
            import traceback
            print("Traceback complet:")
            traceback.print_exc()
            
            raise
    
    print(f"\n🎉 Traitement terminé: {len(event['Records'])} enregistrements")
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'{len(event["Records"])} enregistrements traités')
    }