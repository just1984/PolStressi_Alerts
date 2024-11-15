import json
import os
import logging
from datetime import datetime

def load_last_data(bucket_name, data_file, download_blob):
    try:
        download_blob(bucket_name, data_file, data_file)
        with open(data_file, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def save_last_data(data, bucket_name, data_file, upload_blob):
    with open(data_file, 'w') as f:
        json.dump(data, f)
    upload_blob(bucket_name, data_file, data_file)

def compare_data(old_data, new_data):
    changes_with_emojis = []
    structured_changes = []

    def create_key(item):
        return f"{item['datum']}_{item['von']}_{item['thema']}"

    def is_future_event(item):
        event_date = datetime.strptime(item['datum'], "%d.%m.%Y")
        return event_date > datetime.now()

    old_data_dict = {create_key(item): item for item in old_data if is_future_event(item)}
    new_data_dict = {create_key(item): item for item in new_data if is_future_event(item)}

    def format_change(change_type, item, with_emojis=True):
        emoji = "🟢" if change_type == "New" else "🔴"
        change_text = f"{emoji if with_emojis else change_type} {item['datum']} {item['von']} - {item['thema']}"
        if item.get('plz'):
            change_text += f" - PLZ: {item['plz']}"
        if item.get('strasse_nr'):
            change_text += f", {item['strasse_nr']}"
        if item.get('aufzugsstrecke'):
            change_text += f" - {item['aufzugsstrecke']}"
        return change_text

    for key in new_data_dict:
        if key not in old_data_dict:
            changes_with_emojis.append(format_change("New", new_data_dict[key]))
            structured_changes.append({
                "type": "New",
                "datum": new_data_dict[key]['datum'],
                "von": new_data_dict[key]['von'],
                "thema": new_data_dict[key]['thema'],
                "plz": new_data_dict[key].get('plz'),
                "strasse_nr": new_data_dict[key].get('strasse_nr'),
                "aufzugsstrecke": new_data_dict[key].get('aufzugsstrecke')
            })
        else:
            old_route = old_data_dict[key].get('aufzugsstrecke')
            new_route = new_data_dict[key].get('aufzugsstrecke')
            if old_route != new_route:
                changes_with_emojis.append(f"🔄 Changes in Route: {new_data_dict[key]['datum']} {new_data_dict[key]['von']} - {new_data_dict[key]['thema']}\n\nOld Route: {old_route}\n\nNew Route: {new_route}")
                structured_changes.append({
                    "type": "Modified",
                    "datum": new_data_dict[key]['datum'],
                    "von": new_data_dict[key]['von'],
                    "thema": new_data_dict[key]['thema'],
                    "plz": new_data_dict[key].get('plz'),
                    "strasse_nr": new_data_dict[key].get('strasse_nr'),
                    "alte_aufzugsstrecke": old_route,
                    "neue_aufzugsstrecke": new_route
                })

    for key in old_data_dict:
        if key not in new_data_dict:
            changes_with_emojis.append(format_change("Deleted", old_data_dict[key]))
            structured_changes.append({
                "type": "Deleted",
                "datum": old_data_dict[key]['datum'],
                "von": old_data_dict[key]['von'],
                "thema": old_data_dict[key]['thema'],
                "plz": old_data_dict[key].get('plz'),
                "strasse_nr": old_data_dict[key].get('strasse_nr'),
                "aufzugsstrecke": old_data_dict[key].get('aufzugsstrecke')
            })

    return changes_with_emojis, structured_changes

def save_changes_to_bucket(structured_changes, bucket_name, upload_blob):
    current_time = datetime.now().strftime("%y%m%d_%H:%M")
    backup_file = f"backup/{current_time}.json"
    
    backup_dir = os.path.dirname(backup_file)
    if not os.path.exists(backup_dir):
        logging.info(f"Erstelle Verzeichnis: {backup_dir}")
        os.makedirs(backup_dir)
    
    with open(backup_file, 'w') as f:
        json.dump(structured_changes, f, indent=4, ensure_ascii=False)
        logging.info(f"Datei {backup_file} wurde erfolgreich erstellt.")
    
    upload_blob(bucket_name, backup_file, backup_file)
    logging.info(f"Datei {backup_file} wurde erfolgreich in den Bucket hochgeladen.")
