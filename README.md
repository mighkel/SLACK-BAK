# Slack Channel Export Tool

A Python-based tool for exporting Slack channel messages with built-in anonymization, thread support, and flexible filtering options. Perfect for archiving conversations, compliance needs, or migrating data.

## ✨ Features

- **Multi-Channel Export**: Export one or multiple channels at once (or type 'all')
- **Alphabetically Sorted**: Channels displayed in easy-to-scan alphabetical order
- **Thread Support**: Captures threaded conversations with proper indentation
- **Date Filtering**: Export messages from the last 7, 30, 60, 90 days, or all time
- **Smart File Creation**: Skips empty files if no messages match date range
- **Anonymization**: Automatically replaces usernames with anonymous identifiers (@anon01, @anon02, etc.)
- **Triple Format Output**: JSON (raw data), TXT (human-readable), and optional Markdown
- **File Attachment Downloads**: Optionally download and save all images/files from messages
- **Progress Tracking**: Real-time feedback during export process
- **Rate Limit Handling**: Automatic retry with exponential backoff
- **Reaction Support**: Includes emoji reactions in output
- **Precise Timestamps**: Filenames include date AND time (YYYY-MM-DD-HHMM format)
- **Secure Key Storage**: Generates a separate anonymization key file for reference

## 📋 Requirements

- Python 3.7 or higher
- A Slack workspace where you can create apps
- Member access to the channels you want to export

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install slack-sdk
```

### Step 2: Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Give it a name (e.g., `channel-exporter`) and select your workspace
4. Click **"Create App"**

### Step 3: Configure Permissions

1. In your app settings, click **"OAuth & Permissions"** in the sidebar
2. Scroll down to **"Scopes"** → **"User Token Scopes"**
3. Add the following scopes:

```
channels:history    (View messages in public channels)
channels:read       (View basic channel info)
groups:history      (View messages in private channels)
groups:read         (View basic private channel info)
im:history          (View messages in direct messages)
im:read             (View basic DM info)
mpim:history        (View messages in group DMs)
mpim:read           (View basic group DM info)
users:read          (View user information)
```

### Step 4: Install the App

1. Scroll back to the top of the **"OAuth & Permissions"** page
2. Click **"Install to Workspace"**
3. Review permissions and click **"Allow"**
4. Copy your **User OAuth Token** (starts with `xoxp-`)

### Step 5: Configure the Script

1. Download `slack_channel_export_tool.py`
2. Open it in a text editor
3. Find the **USER SETTINGS** section at the top:

```python
# === USER SETTINGS ===
SLACK_TOKEN = "xoxp-123456789..."        # Paste your token here
OUTPUT_DIR = r"C:\SlackExports\Output"   # Change to your preferred folder
FETCH_THREADS = True                      # Set False to skip threads
INCLUDE_REACTIONS = True                  # Set False to exclude reactions
MAX_RETRIES = 3                          # API retry attempts
# ======================
```

4. Replace `SLACK_TOKEN` with your actual token
5. Update `OUTPUT_DIR` to your preferred save location

### Step 6: Run the Script

```bash
python slack_channel_export_tool.py
```

Follow the interactive prompts to:
1. Select which channel(s) to export
2. Choose your date range filter
3. Wait for the export to complete

## 📖 Usage Examples

### Export a Single Channel (Last 30 Days)

```
📋 Channels available (alphabetical):
  1. 🌐 announcements
  2. 🌐 general
  3. 🔒 project-alpha
  4. 🌐 random

Enter channel number(s): 2

🕓 Select export window:
1. Last 7 days
2. Last 30 days
3. Last 60 days
4. Last 90 days
5. All messages

Enter selection [1-5]: 2
```

### Export Multiple Channels

```
Enter channel number(s): 1,3,4
```

Or type `all` to export every accessible channel.

### Export with File Downloads

Set `DOWNLOAD_FILES = True` in the script, then run normally. You'll see:

```
📥 File downloads enabled - this may take longer

📡 Exporting channel: #general
   → Downloading attachments...
   → Retrieved 247 messages (12 with threads)
   ✅ Saved 2025-01-15-1430-Slack-Export-general.json, 2025-01-15-1430-Slack-Export-general.txt
```

### Handling Empty Results

If no messages match your date filter:

```
📡 Exporting channel: #random
   ⚠️  No messages found in date range - skipping file creation

🧾 EXPORT SUMMARY
───────────────────────────────────────────
Channel                   Messages   Files Created
───────────────────────────────────────────
general                   247        2025-01-15-1430-Slack-Export-general.json, ...
project-alpha             89         2025-01-15-1430-Slack-Export-project-alpha.json, ...

⚠️  Channels with no messages in date range (files not created):
   • random
```

## 📁 Output Files

For each exported channel, the script creates:

### 1. JSON File (Raw Data)
**Format**: `YYYY-MM-DD-HHMM-Slack-Export-{channel}.json`

Example: `2025-01-15-1430-Slack-Export-general.json`

Contains complete message data including:
- Message text and timestamps
- User IDs
- Threaded replies
- Reactions
- File attachments (with local paths if downloaded)
- Message metadata

Perfect for programmatic processing or importing into other tools.

### 2. Text File (Human-Readable)
**Format**: `YYYY-MM-DD-HHMM-Slack-Export-{channel}.txt`

Example output:
```
anon01 [2025-01-15 14:23:11]: Hey team, quick question about the deployment
  Reactions: :thumbsup:3, :eyes:1

anon02 [2025-01-15 14:25:33]: I can help with that!

  ↳ Thread (2 replies):
    anon01 [2025-01-15 14:26:45]: Thanks! When's the best time?
    anon02 [2025-01-15 14:28:12]: How about 3pm today?

anon03 [2025-01-15 15:10:22]: Here's the deployment doc
  📎 File: deployment-guide.pdf (application/pdf) [Saved to: attachments/general/1642271834_deployment-guide.pdf]
```

### 3. Markdown File (Optional, if CREATE_MARKDOWN = True)
**Format**: `YYYY-MM-DD-HHMM-Slack-Export-{channel}.md`

Enhanced formatting with clickable links, perfect for:
- GitHub repositories
- Static site generators (Jekyll, Hugo, MkDocs)
- Documentation tools (GitBook, Docusaurus)
- Reading in any markdown viewer

### 4. Anonymization Key
**Format**: `YYYY-MM-DD-HHMM-anonymization-key.json`

Maps anonymous IDs back to real usernames:
```json
{
  "anon01": "alice",
  "anon02": "bob",
  "anon03": "charlie"
}
```

⚠️ **Keep this file secure!** It's the only way to reverse the anonymization.

### 5. Downloaded Attachments (Optional, if DOWNLOAD_FILES = True)
**Location**: `attachments/{channel-name}/`

Files are named: `{timestamp}_{original-filename}`

**Example structure:**
```
Output/
├── 2025-01-15-1430-Slack-Export-general.json
├── 2025-01-15-1430-Slack-Export-general.txt
├── 2025-01-15-1430-Slack-Export-general.md
├── 2025-01-15-1430-anonymization-key.json
└── attachments/
    ├── general/
    │   ├── 1642271834_screenshot.png
    │   ├── 1642271835_quarterly-report.xlsx
    │   └── 1642271836_presentation.pdf
    └── project-alpha/
        ├── 1642280123_diagram.jpg
        └── 1642280124_requirements.docx
```

## 🔒 Privacy & Anonymization

The tool automatically anonymizes usernames in the text output:
- User mentions `<@U12345>` become `[@anon01]` in text
- In markdown format, they appear as **@anon01**
- Custom emoji `:rocket:` are converted to text `rocket`
- URLs are preserved but cleaned
- Channel mentions become `[channel]`

**What's NOT anonymized:**
- Message content (actual text remains unchanged)
- Timestamps
- File attachments (names preserved)
- The JSON file (contains original user IDs for data integrity)

To fully anonymize, you'll need to manually review message content for sensitive information.

## 🔐 Slack Terms of Service & Legal Compliance

### This Tool is Compliant ✅

This tool uses Slack's official API and is designed for legitimate use:

**Allowed Uses:**
- ✅ Personal backups and archival
- ✅ Compliance and record-keeping
- ✅ Data portability (GDPR rights)
- ✅ Preparing for platform migration
- ✅ Offline reference and documentation

**How We Stay Compliant:**
- Uses official Slack Web API (not scraping)
- Respects workspace permissions and channel membership
- Honors rate limits with automatic backoff
- Only exports data you already have access to
- Can't bypass security or access restricted channels

### Your Responsibilities ⚠️

**Before Using This Tool, Ensure:**
- Your organization allows data exports
- You have permission to backup these conversations
- You comply with applicable privacy laws (GDPR, CCPA, etc.)
- You respect copyright and intellectual property in exported content
- You handle exported data securely

**Slack explicitly supports user-level exports:**
> "If you want to export the contents of your own private groups and direct messages, please see our API documentation."
> — [Slack Help Center](https://slack.com/help/articles/204897248)

### Data Handling Best Practices

1. **Store exports securely** - they may contain sensitive information
2. **Treat anonymization keys like passwords** - they reveal user identities
3. **Delete exports** when no longer needed
4. **Encrypt exports** if containing sensitive data
5. **Don't redistribute** company intellectual property without permission

## ⚙️ Configuration Options

Edit these settings at the top of the script:

| Setting | Default | Description |
|---------|---------|-------------|
| `SLACK_TOKEN` | (required) | Your User OAuth Token from Slack |
| `OUTPUT_DIR` | (required) | Where to save exported files |
| `FETCH_THREADS` | `True` | Include threaded replies (slower but complete) |
| `INCLUDE_REACTIONS` | `True` | Include emoji reactions in output |
| `DOWNLOAD_FILES` | `False` | Download file attachments to local storage |
| `CREATE_MARKDOWN` | `False` | Create .md formatted output (great for GitHub/static sites) |
| `MAX_RETRIES` | `3` | Number of retry attempts for API failures |

### File Downloads Feature

When `DOWNLOAD_FILES = True`:
- Creates `attachments/[channel-name]/` subdirectory
- Downloads all images, documents, and files from messages
- Names files: `[timestamp]_[original-filename]`
- Updates file references in JSON and text outputs
- **Note**: This increases export time and disk usage

### Markdown Export Feature

When `CREATE_MARKDOWN = True`:
- Creates a `.md` file alongside JSON/TXT
- Perfect for viewing on GitHub, static site generators, or documentation tools
- Features:
  - Proper markdown headers and formatting
  - Clickable file links to downloaded attachments
  - Bold usernames and formatted reactions
  - Code blocks preserved
  - Thread hierarchy with indentation

**Example markdown output:**
```markdown
# Channel: #general

Exported: 2025-01-15 14:30:00

---

**@anon01** [2025-01-15 14:23:11]: Hey team, quick question about the deployment
*Reactions: :thumbsup: :eyes:*

**@anon02** [2025-01-15 14:25:33]: I can help with that!

  *↳ Thread (2 replies):*

  **@anon01** [2025-01-15 14:26:45]: Thanks! When's the best time?
  **@anon02** [2025-01-15 14:28:12]: How about 3pm today?
```

## 🐛 Troubleshooting

### Error: "No channels found or token missing proper read scopes"

**Solution**: 
- Verify you added all required scopes (see Step 3)
- Reinstall the app to workspace after adding scopes
- Make sure you copied the **User OAuth Token**, not Bot Token

### Error: "invalid_auth" or "not_authed"

**Solution**:
- Your token may have expired or been revoked
- Generate a new token by reinstalling the app
- Ensure you're using the token that starts with `xoxp-`

### Error: "channel_not_found"

**Solution**:
- You must be a member of the channel to export it
- Private channels require you to be explicitly added
- Ask a workspace admin to invite you to the channel

### Export is Very Slow

**Possible causes**:
- Large channels (10,000+ messages)
- Thread fetching is enabled for channels with many threads
- File downloads enabled with many attachments
- Slack API rate limiting

**Solutions**:
- Set `FETCH_THREADS = False` for faster exports (skips thread replies)
- Set `DOWNLOAD_FILES = False` if you don't need attachments
- Export smaller date ranges
- The script handles rate limits automatically, just wait it out

### File Download Failures

**Symptoms**: Warning messages like "Failed to download file"

**Common causes**:
- File was deleted from Slack
- File URL expired (very old messages)
- Network connectivity issues
- Permission issues with output directory

**Solutions**:
- Check internet connection
- Ensure `OUTPUT_DIR` has write permissions
- Old files (>90 days) may have expired URLs - this is normal
- The export continues even if individual files fail

### Error: "ratelimited"

**Solution**: The script automatically retries with exponential backoff. Just wait - this is normal for large exports.

### Script Crashes Mid-Export

**Solution**:
- Check your internet connection
- Increase `MAX_RETRIES` in settings
- Try exporting fewer channels at once
- Reduce date range to export less data

## 🔐 Security Considerations

1. **Token Security**: 
   - Never commit your token to version control
   - Add `config.json` to `.gitignore`
   - Consider using environment variables for production
   - Tokens can be revoked from Slack App settings if compromised

2. **Output Files**: 
   - May contain sensitive conversations and attachments
   - Store in encrypted locations if necessary
   - Set appropriate file permissions (`chmod 600` on Unix)

3. **Anonymization Key**: 
   - Keep separate from anonymized exports
   - Treat like a password - it reveals user identities
   - Consider encrypting this file

4. **Workspace Policies**: 
   - Check your organization's data retention policies
   - Some industries have specific export restrictions
   - When in doubt, ask your IT/compliance team

5. **Downloaded Attachments**:
   - May contain malware if from untrusted sources
   - Scan downloads with antivirus if exporting old channels
   - Respect copyright and licensing of downloaded files

## 🎯 Use Cases

- **Compliance & Archival**: Keep permanent records of important conversations
- **Data Migration**: Move discussions to another platform
- **Analysis**: Analyze communication patterns or sentiment
- **Backup**: Create local backups of critical channels
- **Offboarding**: Archive project channels before deletion
- **Legal/HR**: Preserve conversations for documentation

## 🛠️ Advanced Usage

### Using as a Module

```python
from slack_channel_export_tool import SlackExporter

exporter = SlackExporter(
    token="xoxp-your-token",
    output_dir="/path/to/exports"
)
exporter.load_users()
channels = exporter.get_channels()

# Export specific channel
channel = channels[0]
result = exporter.export_channel(channel, cutoff_ts=None)
```

### Automation with Cron/Task Scheduler

Create a shell script for weekly backups:

```bash
#!/bin/bash
cd /path/to/script
python slack_channel_export_tool.py <<EOF
all
2
EOF
```

Then schedule it:
```bash
# Weekly export every Sunday at 2 AM
0 2 * * 0 /path/to/export_script.sh
```

### Export to Other Formats

The JSON output is structured and easy to convert:

```python
import json
import csv

# Convert to CSV
with open('export.json') as f:
    messages = json.load(f)

with open('export.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['user', 'text', 'ts'])
    writer.writeheader()
    for msg in messages:
        writer.writerow({
            'user': msg.get('user', ''),
            'text': msg.get('text', ''),
            'ts': msg.get('ts', '')
        })
```

## 📝 Limitations

- **Only exports channels you're a member of** - Cannot access channels you're not in
- **No file downloads** - File metadata is saved, but files themselves aren't downloaded
- **Message edits** - Only the current version of messages is exported (edit history not included)
- **Deleted messages** - Cannot export messages that have been deleted
- **Workspace restrictions** - Some workspaces may block custom app creation

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- File attachment downloading
- Export to additional formats (HTML, PDF, Markdown)
- GUI interface
- Incremental exports (only new messages since last export)
- Message search/filtering
- Progress bars for large exports

## ⚠️ Important Notes

- **This tool is not affiliated with Slack Technologies, Inc.**
- Designed for legitimate backup, compliance, and archival purposes
- Users are responsible for complying with their organization's policies
- Always handle exported data according to applicable privacy laws
- The tool uses official Slack APIs and respects all workspace permissions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**What this means:**
- ✅ Free to use for personal and commercial purposes
- ✅ You can modify and distribute the code
- ✅ No warranty provided - use at your own risk
- ✅ Attribution appreciated but not required for use

## 🔗 Resources

- [Slack API Documentation](https://api.slack.com/docs)
- [OAuth Scopes Reference](https://api.slack.com/scopes)
- [Rate Limit Guidelines](https://api.slack.com/docs/rate-limits)
- [slack-sdk Python Package](https://slack.dev/python-slack-sdk/)

## 📧 Support

For issues specific to this tool, please check the troubleshooting section above. For Slack API questions, refer to [Slack's API documentation](https://api.slack.com/docs).

---

**Version**: 2.0  (cAI v9)
**Last Updated**: October 2025  
**Python**: 3.7+  
**Dependencies**: slack-sdk
