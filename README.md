### 🚀 Automated Backup & Rotation with Google Drive Integration
📌 Overview

This project provides a fully automated backup solution with Google Drive integration.

Key Features:

📦 Compresses project files into .tar.gz archives

☁️ Uploads backups to Google Drive using rclone

🔄 Implements a retention policy (daily, weekly, monthly rotation)

📝 Maintains detailed logs with timestamps

🔔 Sends optional webhook notifications after successful backups

⏰ Supports cron job scheduling for hands-free automation

⚙️ Requirements

Python 3.x

rclone
 (configured with Google Drive)

Linux environment (Ubuntu recommended)

🛠️ Installation & Setup
1. Clone the Repository
git clone https://github.com/<your-username>/Automated-Backup-Project.git
cd Automated-Backup-Project

2. Install Dependencies
sudo apt update
sudo apt install rclone python3

3. Configure Rclone with Google Drive
rclone config


Choose n for new remote

Name: gdrive

Storage: Google Drive

Follow on-screen instructions to authenticate

⚙️ Configuration

Edit config.json to define your project settings:

{
  "project_dir": "/home/ubuntu/backups/MyApp",
  "project_name": "MyApp",
  "remote": "gdrive",
  "remote_path": "Backups/MyProject",
  "webhook_url": "https://webhook.site/your-unique-url",
  "retention": {
    "daily": 7,
    "weekly": 4,
    "monthly": 3
  }
}

Config Parameters

project_dir → Path to project files

project_name → Name of project (used in backup filename)

remote → Remote name from rclone config

remote_path → Destination path in Google Drive

webhook_url → Webhook URL for notifications (optional)

retention → Number of daily, weekly, monthly backups to keep

▶️ Usage
Run Manually
python3 backup.py --config config.json

Run Without Webhook Notifications
python3 backup.py --config config.json --no-notify

⏰ Automating with Cron

Add this line to your crontab (crontab -e):

0 2 * * * python3 /home/ubuntu/Automated-Backup-Project/backup.py --config /home/ubuntu/Automated-Backup-Project/config.json >> /home/ubuntu/backups/backup.log 2>&1


This will run the backup daily at 2:00 AM.

📄 Example Backup Log
[2025-08-20 02:00:01] Backup started.
[2025-08-20 02:00:02] Created archive: MyApp_2025-08-20_0200.tar.gz
[2025-08-20 02:00:05] Uploaded to Google Drive: Backups/MyProject/MyApp_2025-08-20_0200.tar.gz
[2025-08-20 02:00:05] Deletion Summary: Removed 1 old daily backup.
[2025-08-20 02:00:06] Webhook notification sent successfully.
[2025-08-20 02:00:06] Backup completed successfully.

🌐 Webhook Notification

If enabled, the script sends a JSON payload:

curl -X POST -H "Content-Type: application/json" \
-d '{"project": "MyApp", "date": "2025-08-20 02:00:06", "status": "Backup Successful"}' \
https://webhook.site/your-unique-url

🔐 Security Best Practices

Store rclone config securely (~/.config/rclone/rclone.conf)

Use service accounts for production instead of personal Google Drive authentication

Keep config.json or .env outside public repos (or add to .gitignore)

Test retention rules carefully before applying to production backups
