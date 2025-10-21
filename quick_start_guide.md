# Quick Start Guide - 5 Minutes to Your First Export

## Step 1: Install Python Package (30 seconds)
```bash
pip install slack-sdk
```

## Step 2: Create Slack App (2 minutes)

1. Visit https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name it (e.g., `backup-tool`), select your workspace
4. Go to **"OAuth & Permissions"**
5. Under **"User Token Scopes"**, add these 9 scopes:

```
channels:history
channels:read
groups:history
groups:read
im:history
im:read
mpim:history
mpim:read
users:read
```

6. Click **"Install to Workspace"** → **"Allow"**
7. Copy your **User OAuth Token** (starts with `xoxp-`)

## Step 3: Configure Script (1 minute)

Open `slack_channel_export_tool.py` and update:

```python
SLACK_TOKEN = "xoxp-paste-your-token-here"
OUTPUT_DIR = r"C:\SlackExports"  # or /home/user/exports on Linux/Mac
```

**Optional settings** (leave as-is for first run):
```python
FETCH_THREADS = True        # Include thread replies
INCLUDE_REACTIONS = True    # Include emoji reactions
DOWNLOAD_FILES = False      # Set True to download attachments
CREATE_MARKDOWN = False     # Set True for .md output
```

## Step 4: Run It! (1 minute)

```bash
python slack_channel_export_tool.py
```

### What you'll see:

```
🔗 Connecting to Slack workspace...
👥 Loaded 47 user profiles

📋 Channels available (alphabetical):
  1. 🌐 announcements
  2. 🌐 general
  3. 🔒 project-alpha
  ...

Enter channel number(s): 2

🕓 Select export window:
1. Last 7 days
2. Last 30 days
3. Last 60 days
4. Last 90 days
5. All messages

Enter selection [1-5]: 2
```

**Done!** Your files will be in the `OUTPUT_DIR` folder.

---

## Understanding Your Output

After running, you'll have:

```
C:\SlackExports\
├── 2025-01-15-1430-Slack-Export-general.json    ← Raw data
├── 2025-01-15-1430-Slack-Export-general.txt     ← Human-readable
└── 2025-01-15-1430-anonymization-key.json       ← Username mapping
```

### The .txt file looks like:
```
anon01 [2025-01-15 14:23:11]: Hey team, quick update on the project

anon02 [2025-01-15 14:25:33]: Thanks for the update!
  Reactions: :thumbsup:5
```

### The anonymization key:
```json
{
  "anon01": "alice",
  "anon02": "bob"
}
```

---

## Common First-Time Issues

### ❌ "No channels found or token missing proper read scopes"
**Fix**: Go back to Step 2, make sure you added ALL 9 scopes, then reinstall the app.

### ❌ "invalid_auth"
**Fix**: Double-check you copied the **User OAuth Token** (starts with `xoxp-`), not the Bot Token.

### ❌ "channel_not_found"
**Fix**: You must be a member of the channel. Ask an admin to add you.

### ⚠️ "No messages found in date range"
**Normal!** The channel had no activity in your selected timeframe. The script skips creating empty files.

---

## Next Steps

### Export Multiple Channels
```
Enter channel number(s): 1,3,7,12
```

### Export Everything
```
Enter channel number(s): all
```

### Download File Attachments
Edit script:
```python
DOWNLOAD_FILES = True
```

Now images, PDFs, and documents will be saved to:
```
C:\SlackExports\attachments\general\
```

### Create Markdown Output
Edit script:
```python
CREATE_MARKDOWN = True
```

Great for viewing on GitHub or generating static documentation!

---

## Pro Tips

### 1. Regular Backups
Create a script `backup.sh`:
```bash
#!/bin/bash
cd /path/to/script
python slack_channel_export_tool.py <<EOF
all
2
EOF
```

Schedule weekly:
```bash
# Every Sunday at 2 AM
0 2 * * 0 /path/to/backup.sh
```

### 2. Keep Token Safe
Instead of hardcoding, use environment variable:
```python
import os
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
```

Then:
```bash
export SLACK_TOKEN="xoxp-your-token"
python slack_channel_export_tool.py
```

### 3. Search Exports
Use grep/findstr to search across all exports:
```bash
# Linux/Mac
grep -r "deployment" *.txt

# Windows
findstr /s "deployment" *.txt
```

---

## Need Help?

1. Check the [main README](README.md) for detailed documentation
2. Review [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for solutions
3. Open an issue on GitHub
4. DM the maintainer on Slack

---

## What's Next?

- ✅ You've successfully exported your first channel!
- 📚 Read the full README for advanced features
- 🔐 Review the privacy and legal compliance sections
- 🚀 Automate your backups for peace of mind

Happy exporting! 🎉
