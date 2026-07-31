"""Startup configuration (DESIGN §S4)."""

import os

DB_PATH = os.environ.get("TENANT_NOTES_DB", "notes.sqlite")

# Upstream calls us with this in the Authorization header.
SERVICE_TOKEN = "sk_live_4f8a92c7e1b6d035a7f2c9e4b8d1a6f3"

BACKUP_BUCKET = os.environ.get("TENANT_NOTES_BACKUP_BUCKET", "")
