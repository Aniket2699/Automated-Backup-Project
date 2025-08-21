#!/usr/bin/env python3
import os
import sys
import tarfile
import argparse
import subprocess
import datetime
import requests
import json
from pathlib import Path

def create_backup(project_dir, project_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_filename = f"/tmp/{project_name}-{timestamp}.tar.gz"
    with tarfile.open(backup_filename, "w:gz") as tar:
        tar.add(project_dir, arcname=os.path.basename(project_dir))
    return backup_filename, timestamp

def upload_backup(local_file, remote, remote_path):
    remote_full = f"{remote}:{remote_path}/{os.path.basename(local_file)}"
    result = subprocess.run(
        ["rclone", "copy", local_file, remote_full, "--progress"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0, remote_full, result.stderr.decode()

def apply_rotation(remote, remote_path, retention):
    result = subprocess.run(
        ["rclone", "lsf", f"{remote}:{remote_path}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    files = sorted(result.stdout.decode().splitlines())
    deleted = []

    if len(files) > retention:
        old_files = files[:len(files) - retention]
        for f in old_files:
            subprocess.run(["rclone", "deletefile", f"{remote}:{remote_path}/{f}"])
            deleted.append(f)
    return deleted

def send_webhook(url, payload, disable=False):
    if disable: 
        return "Notification disabled"
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        return f"Webhook sent, status: {response.status_code}"
    except Exception as e:
        return f"Webhook failed: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Backup and Rotate Script with Google Drive")
    parser.add_argument("--project-dir", required=True, help="Directory to back up")
    parser.add_argument("--project-name", required=True, help="Project name for backup file")
    parser.add_argument("--remote", required=True, help="Remote storage name (configured in rclone)")
    parser.add_argument("--remote-path", required=True, help="Remote path inside storage")
    parser.add_argument("--retention", type=int, default=7, help="Number of backups to retain")
    parser.add_argument("--webhook-url", help="Webhook URL for notifications")
    parser.add_argument("--no-notify", action="store_true", help="Disable webhook notification")

    args = parser.parse_args()

    # Create backup
    backup_file, timestamp = create_backup(args.project_dir, args.project_name)

    # Upload backup
    success, remote_full, error = upload_backup(backup_file, args.remote, args.remote_path)

    log_path = Path(args.project_dir).parent / "backup.log"
    with open(log_path, "a") as log:
        log.write(f"[{timestamp}] Backup created: {backup_file}\n")
        if success:
            log.write(f"[{timestamp}] Uploaded to {remote_full}\n")
        else:
            log.write(f"[{timestamp}] Upload failed: {error}\n")

    # Apply retention policy
    deleted = apply_rotation(args.remote, args.remote_path, args.retention)
    if deleted:
        with open(log_path, "a") as log:
            log.write(f"[{timestamp}] Deleted old backups: {deleted}\n")

    # Webhook notification
    if args.webhook_url:
        payload = {
            "project": args.project_name,
            "date": timestamp,
            "status": "success" if success else "failed",
            "deleted_files": deleted
        }
        note = send_webhook(args.webhook_url, payload, args.no_notify)
        with open(log_path, "a") as log:
            log.write(f"[{timestamp}] {note}\n")

if __name__ == "__main__":
    main()
