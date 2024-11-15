import hashlib
import requests
import logging
import json
import pytz
from datetime import datetime
from storage_utils import upload_blob, download_blob
from data_utils import load_last_data, save_last_data, compare_data, save_changes_to_bucket
from email_utils import send_email, split_and_send_email

with open('config.json') as config_file:
    config = json.load(config_file)

url = 'https://www.berlin.de/polizei/service/versammlungsbehoerde/versammlungen-aufzuege/index.php/index/all.json'
bucket_name = 'YOUR_NAME_HERE'
data_file = 'last_data.json'
hash_file = 'hash.txt'

def fetch_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.content
        
        current_hash = hashlib.sha256(content).hexdigest()
        
        try:
            download_blob(bucket_name, hash_file, hash_file)
            with open(hash_file, 'r') as f:
                stored_hash = f.read().strip()
        except Exception as e:
            logging.warning(f"Kein gespeicherter Hashwert gefunden: {e}")
            stored_hash = None

        if current_hash == stored_hash:
            return None, current_hash, False

        with open(hash_file, 'w') as f:
            f.write(current_hash)
        upload_blob(bucket_name, hash_file, hash_file)
        
        return response.json(), current_hash, stored_hash is not None
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Daten: {e}")
        return None, None, False

def main(request):
    logging.basicConfig(level=logging.INFO)
    
    try:
        fetched_data, content_hash, hash_changed = fetch_data()
        
        # ÄNDERUNG ZEITZONE ?!
        berlin_tz = pytz.timezone('Europe/Berlin')
        current_time = datetime.now(berlin_tz).strftime("%d.%m.%Y_%H:%M")

        shortened_hash = content_hash[:12]
        
        if fetched_data is None:
            logging.info("Keine neuen Daten vorhanden oder Fehler beim Abrufen der Daten.")
            return 'No new data or error fetching data.', 200
        
        if 'index' not in fetched_data:
            logging.error("Erwarteter Schlüssel 'index' nicht in den heruntergeladenen Daten gefunden.")
            return 'Invalid data format.', 500
        
        current_data = fetched_data['index']
        last_data = load_last_data(bucket_name, data_file, download_blob)
        
        if last_data is None:
            save_last_data(current_data, bucket_name, data_file, upload_blob)
            logging.info("Initialer Datenabruf.")
            return 'Initial data fetched and stored.', 200
        
        changes_with_emojis, structured_changes = compare_data(last_data, current_data)
        
        if structured_changes:
            logging.info(f"Änderungen festgestellt: {structured_changes}")
            save_last_data(current_data, bucket_name, data_file, upload_blob)
            subject = f"PolDatenbank_Änderungen {current_time} #polizeistressiupdates"
            
            changes_str = "\n\n".join(changes_with_emojis)
            body = f"{current_time}\n{len(changes_with_emojis)} Changes (🟢 new, 🔴 deleted)\nHash: {shortened_hash}\n\n{changes_str}"
            
            split_and_send_email(subject, body)
            save_changes_to_bucket(structured_changes, bucket_name, upload_blob)
            return 'Changes detected, email sent, and backup saved.', 200
        else:
            if hash_changed:
                logging.info("Keine Änderungen festgestellt, aber Hashwert hat sich geändert.")
                subject = f"PolDatenbank_Keine_Änderungen {current_time} #polizeistressiupdates"
                body = f"{current_time}\nDatenbankupdate ohne Änderungen\nHash: {shortened_hash}"
                send_email(subject, body)
            return 'No changes detected.', 200
    
    except Exception as e:
        logging.error(f"Fehler beim Verarbeiten der Daten: {e}", exc_info=True)
        return str(e), 500

if __name__ == "__main__":
    main(None)