# Slack App Description

## For Slack App Manager

**App Name:** Channel Export Tool

**Short Description (80 chars max):**
Personal backup tool for exporting channel messages with privacy features

**Full Description:**

This app enables personal backup and archival of Slack channel conversations. It exports messages to JSON, TXT, and optionally Markdown formats with built-in anonymization features for privacy protection.

**Key Features:**
- Export public and private channels you're a member of
- Date range filtering (7, 30, 60, 90 days, or all time)
- Thread capture with proper formatting
- Optional file attachment downloads
- Anonymizes usernames in text output
- Generates mapping key for de-anonymization when needed
- Multiple output formats (JSON, TXT, MD)

**Use Cases:**
- Personal message archival
- Compliance and record-keeping
- Project documentation
- Data migration preparation
- Offline reference

**Data Usage:**
This app only accesses channels you're already a member of. It uses Slack's official API and respects all workspace permissions. Exported data is stored locally on your machine - nothing is sent to external servers.

**Support:**
For questions or to request a copy of the export script, please DM [your-username] or visit the GitHub repository at [your-repo-url].

**Technical Requirements:**
- Python 3.7+
- slack-sdk library
- User OAuth token with appropriate scopes

This app is provided as-is for legitimate backup and archival purposes. Users are responsible for complying with their organization's data policies and applicable privacy regulations.

---

## For Your README Badge/Header

```
🔐 Personal Slack Channel Export Tool
Backup and archive your Slack conversations with built-in privacy features
```

## One-Liner for Social/Quick Description

"A Python tool for backing up Slack channels to JSON/TXT/MD with user anonymization - perfect for personal archives, compliance, or migration prep."
