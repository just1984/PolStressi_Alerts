# POLIZEI STRESSI _ UPDATES (ALERT SYSTEM)

Changes to the database of Berlin's Versammlungsbehörde are shared on this Telegram channel: https://t.me/polizeistressiupdates.

This repository contains the code behind this functionality. It’s a Python-based program that monitors the data, detects updates, and sends notifications via email. The data is sourced from a public API provided by the Berlin Police, focusing on public assemblies and demonstrations. Additionally, an external service (IFTTT) is used to publish the contents of sent emails to the Telegram channel.

## Features

- **Automated Data Fetching**: Downloads JSON data from a predefined URL.
- **Change Detection**:
  - Identifies new, modified, or deleted entries.
  - Compares previous and current data states.
- **Cloud Integration**:
  - Uses Google Cloud Storage for saving data and hash files.
  - Backs up detected changes in a JSON file.
- **Email Notifications**:
  - Sends detailed change notifications to a configured email.
  - Supports splitting long messages into multiple emails.
- **Localized Timezone Handling**: Adapts to Berlin's time zone (`Europe/Berlin`).

## How It Works

1. The script fetches data from a public API and calculates a hash to detect changes.
2. If changes are detected:
   - The script compares new data with the previous state.
   - Detected changes are formatted with visual markers (e.g., 🟢 for new, 🔴 for deleted and 🔄 for changed).
   - Notifications are sent via email, and a backup of changes is stored in Google Cloud Storage.
3. If no changes are found, a "no changes" notification is optionally sent.

## Configuration

1. Create a `config.json` file with the following structure:

   ```json
   {
     "email": "your_email@gmail.com",
     "password": "your_email_password",
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "to_email": "recipient_email@gmail.com"
   }
   ```
   
2. Update the `bucket_name` in `main.py`.

## Usage

1. Upload files to a server (eg Google Cloud Run)
2. Set up a scheduler (e.g., Cron or Task Scheduler) for periodic execution if needed.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.