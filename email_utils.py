import logging
import smtplib
import pytz
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime
import time

with open('config.json') as config_file:
    config = json.load(config_file)

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = config['email']
    msg['To'] = config['to_email']
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email'], config['password'])
        text = msg.as_string()
        server.sendmail(config['email'], config['to_email'], text)
        server.quit()
        logging.info("E-Mail erfolgreich gesendet.")
    except Exception as e:
        logging.error(f"Fehler beim Senden der E-Mail: {e}")

def split_and_send_email(subject, body):
    max_length = 4000
    if len(body) <= max_length:
        send_email(subject, body)
    else:
        parts = [body[i:i + max_length] for i in range(0, len(body), max_length)]
        total_parts = len(parts)
        
        berlin_tz = pytz.timezone('Europe/Berlin')
        current_time = datetime.now(berlin_tz).strftime("%y%m%d_%H:%M")
        
        for i, part in enumerate(parts):
            part_subject = f"{subject} ({i+1}/{total_parts})"
            send_email(part_subject, part)
            
            if i < total_parts - 1:  
                logging.info(f"Warte 10 Sekunden, bevor die naechste E-Mail gesendet wird...")
                time.sleep(10)
