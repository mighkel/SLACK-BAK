# slack_channel_export_tool.py
"""
Slack Channel Export Tool
Exports Slack channel messages with anonymization, thread support, and flexible filtering.

LICENSE: MIT License
Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

USAGE NOTICE: This tool uses Slack's official API to export data that you have legitimate
access to. Users are responsible for:
- Complying with their organization's data retention and export policies
- Respecting Slack's Terms of Service (https://slack.com/terms-of-service)
- Handling exported data according to applicable privacy laws (GDPR, CCPA, etc.)
- Not using this tool to bypass workspace security or access restrictions
- Keeping sensitive exported data secure

This tool is provided for legitimate backup, compliance, and archival purposes only.
"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json, re, os, time, sys, logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

# Try to import requests for better file downloads
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  'requests' library not found. File downloads will be limited.")
    print("   Install with: pip install requests")
    print()

# === USER SETTINGS ===
SLACK_TOKEN = "xoxp-123456789..."        # Paste your Slack user token here
OUTPUT_DIR = r"C:\SlackExports\Output"   # Folder to save output files (edit as needed)
FETCH_THREADS = True                      # Set to False to skip threaded replies (faster)
INCLUDE_REACTIONS = True                  # Include emoji reactions in output
DOWNLOAD_FILES = False                    # Set to True to download file attachments (slower, uses disk space)
CREATE_MARKDOWN = False                   # Set to True to create .md formatted output
ENABLE_LOGGING = True                     # Set to True to create detailed log files
MAX_RETRIES = 3                          # Number of retries for API calls
# ======================

# Configure logging if enabled
if ENABLE_LOGGING:
    log_filename = os.path.join(OUTPUT_DIR, f"slack_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
else:
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

class SlackExporter:
    def __init__(self, token: str, output_dir: str):
        self.client = WebClient(token=token)
        self.output_dir = output_dir
        self.id_to_name = {}
        self.anon_map = {}
        self.anon_counter = 1
        os.makedirs(output_dir, exist_ok=True)
        
    def retry_api_call(self, func, *args, **kwargs):
        """Retry API calls with exponential backoff."""
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except SlackApiError as e:
                if e.response["error"] == "ratelimited":
                    wait_time = int(e.response.headers.get("Retry-After", 2 ** attempt))
                    print(f"⏳ Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    if attempt == MAX_RETRIES - 1:
                        raise
                    print(f"⚠️  API error: {e.response['error']}. Retrying...")
                    time.sleep(2 ** attempt)
        raise Exception("Max retries exceeded")

    def load_users(self):
        """Load all users from the workspace."""
        print("\n🔗 Connecting to Slack workspace...")
        logger.info("Starting user list retrieval")
        users, cursor = [], None
        while True:
            resp = self.retry_api_call(self.client.users_list, cursor=cursor)
            users.extend(resp["members"])
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        self.id_to_name = {
            u["id"]: u.get("profile", {}).get("display_name") or u.get("name") 
            for u in users
        }
        print(f"👥 Loaded {len(self.id_to_name)} user profiles")
        logger.info(f"Successfully loaded {len(self.id_to_name)} user profiles")

    def get_channels(self) -> List[Dict]:
        """Retrieve all accessible channels, sorted alphabetically."""
        channels, cursor = [], None
        while True:
            resp = self.retry_api_call(
                self.client.conversations_list, 
                types="public_channel,private_channel", 
                cursor=cursor, 
                limit=200
            )
            channels.extend(resp["channels"])
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        if not channels:
            raise SystemExit("❌ No channels found or token missing proper read scopes.")
        
        # Sort alphabetically by channel name
        channels.sort(key=lambda c: c['name'].lower())
        return channels

    def anon_id(self, uid: str) -> str:
        """Convert user ID to anonymous identifier."""
        if uid not in self.anon_map:
            self.anon_map[uid] = f"anon{self.anon_counter:02d}"
            self.anon_counter += 1
        return self.anon_map[uid]

    def clean_text(self, text: str, format_type: str = "text") -> str:
        """Sanitize message text by removing/replacing sensitive content."""
        # Replace user mentions with anonymous IDs
        if format_type == "markdown":
            text = re.sub(r"<@(U[0-9A-Z]+)>", lambda m: f"**@{self.anon_id(m.group(1))}**", text)
        else:
            text = re.sub(r"<@(U[0-9A-Z]+)>", lambda m: f"[@{self.anon_id(m.group(1))}]", text)
        
        # Remove custom emoji markers (keep text between colons)
        text = re.sub(r":(\w+):", r"\1", text)
        # Clean up URLs
        text = re.sub(r"<(http[^>|]+)(\|[^>]+)?>", r"\1", text)
        # Remove channel mentions
        text = re.sub(r"<#[^>]+>", "[channel]", text)
        return text.strip()

    def download_file(self, file_info: Dict, channel_name: str, msg_ts: str) -> Optional[str]:
        """Download a file attachment to local storage."""
        if not DOWNLOAD_FILES:
            return None
        
        if not HAS_REQUESTS:
            logger.warning("Cannot download files without 'requests' library installed")
            return None
        
        try:
            # Get download URL
            url = file_info.get("url_private_download") or file_info.get("url_private")
            if not url:
                logger.warning(f"No download URL found for file: {file_info.get('name', 'unknown')}")
                return None
            
            # Create attachments directory
            attach_dir = os.path.join(self.output_dir, "attachments", channel_name)
            os.makedirs(attach_dir, exist_ok=True)
            
            # Generate safe filename
            original_name = file_info.get("name", "unknown")
            timestamp = msg_ts.replace(".", "_")
            safe_filename = f"{timestamp}_{original_name}"
            local_path = os.path.join(attach_dir, safe_filename)
            
            # Download with authentication
            headers = {"Authorization": f"Bearer {self.client.token}"}
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {original_name}")
            return os.path.relpath(local_path, self.output_dir)
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to download {file_info.get('name', 'unknown')}: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error downloading file: {str(e)}")
            return None

    def fetch_thread_replies(self, channel_id: str, thread_ts: str) -> List[Dict]:
        """Fetch all replies in a thread."""
        try:
            resp = self.retry_api_call(
                self.client.conversations_replies,
                channel=channel_id,
                ts=thread_ts,
                limit=100
            )
            # Skip the parent message (first item)
            return resp["messages"][1:] if len(resp["messages"]) > 1 else []
        except SlackApiError:
            return []

    def fetch_messages(self, channel_id: str, cutoff_ts: Optional[float]) -> List[Dict]:
        """Fetch all messages from a channel with optional date filter."""
        messages, cursor = [], None
        while True:
            resp = self.retry_api_call(
                self.client.conversations_history,
                channel=channel_id,
                cursor=cursor,
                limit=200
            )
            batch = resp["messages"]
            
            # Apply date filter if specified
            if cutoff_ts:
                batch = [m for m in batch if float(m["ts"]) >= cutoff_ts]
            
            # Fetch threaded replies if enabled
            if FETCH_THREADS:
                for msg in batch:
                    if msg.get("reply_count", 0) > 0:
                        replies = self.fetch_thread_replies(channel_id, msg["ts"])
                        msg["thread_messages"] = replies
            
            messages.extend(batch)
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return messages

    def format_message_text(self, msg: Dict, indent: int = 0, format_type: str = "text") -> str:
        """Format a single message for text or markdown output."""
        uid = msg.get("user", "system")
        anon = self.anon_id(uid) if uid != "system" else "System"
        text = self.clean_text(msg.get("text", ""), format_type)
        ts = datetime.fromtimestamp(float(msg["ts"])).strftime("%Y-%m-%d %H:%M:%S")
        
        if format_type == "markdown":
            prefix = "  " * indent
            output = f"{prefix}**{anon}** [{ts}]: {text}\n"
            
            # Add reactions
            if INCLUDE_REACTIONS and msg.get("reactions"):
                reactions = " ".join([f":{r['name']}:" for r in msg["reactions"]])
                output += f"{prefix}*Reactions: {reactions}*\n"
            
            # Add code blocks if present
            if msg.get("blocks"):
                for block in msg["blocks"]:
                    if block.get("type") == "rich_text":
                        for element in block.get("elements", []):
                            if element.get("type") == "rich_text_preformatted":
                                code = "\n".join([e.get("text", "") for e in element.get("elements", [])])
                                output += f"{prefix}```\n{code}\n```\n"
            
            # Add file info
            if msg.get("files"):
                for f in msg["files"]:
                    fname = f.get('name', 'unnamed')
                    ftype = f.get('mimetype', 'unknown')
                    local_path = f.get('local_path')
                    if local_path:
                        output += f"{prefix}📎 [{fname}]({local_path}) ({ftype})\n"
                    else:
                        output += f"{prefix}📎 {fname} ({ftype})\n"
        else:
            # Plain text format
            prefix = "  " * indent
            output = f"{prefix}{anon} [{ts}]: {text}"
            
            if INCLUDE_REACTIONS and msg.get("reactions"):
                reactions = ", ".join([f":{r['name']}:{r['count']}" for r in msg["reactions"]])
                output += f"\n{prefix}  Reactions: {reactions}"
            
            if msg.get("files"):
                for f in msg["files"]:
                    fname = f.get('name', 'unnamed')
                    ftype = f.get('mimetype', 'unknown')
                    local_path = f.get('local_path')
                    if local_path:
                        output += f"\n{prefix}  📎 File: {fname} ({ftype}) [Saved to: {local_path}]"
                    else:
                        output += f"\n{prefix}  📎 File: {fname} ({ftype})"
        
        return output

    def export_channel(self, channel: Dict, cutoff_ts: Optional[float], timestamp_str: str) -> tuple:
        """Export a single channel's messages."""
        cname = channel["name"]
        print(f"📡 Exporting channel: #{cname}")
        logger.info(f"Starting export for channel: #{cname}")
        
        messages = self.fetch_messages(channel["id"], cutoff_ts)
        
        # Download files if enabled
        if DOWNLOAD_FILES and messages:
            print(f"   → Downloading attachments...")
            logger.info(f"Downloading attachments for #{cname}")
            file_count = 0
            for msg in messages:
                if msg.get("files"):
                    for file_info in msg["files"]:
                        local_path = self.download_file(file_info, cname, msg["ts"])
                        if local_path:
                            file_info["local_path"] = local_path
                            file_count += 1
            if file_count > 0:
                logger.info(f"Downloaded {file_count} files for #{cname}")
        
        msg_count = len(messages)
        thread_count = sum(1 for m in messages if m.get("thread_messages"))
        
        # Skip if no messages
        if msg_count == 0:
            print(f"   ⚠️  No messages found in date range - skipping file creation")
            logger.info(f"No messages found for #{cname} in date range")
            return (cname, 0, None, None, None)
        
        print(f"   → Retrieved {msg_count} messages ({thread_count} with threads)")
        logger.info(f"Retrieved {msg_count} messages ({thread_count} with threads) for #{cname}")
        
        json_name = f"{timestamp_str}-Slack-Export-{cname}.json"
        txt_name = f"{timestamp_str}-Slack-Export-{cname}.txt"
        md_name = f"{timestamp_str}-Slack-Export-{cname}.md" if CREATE_MARKDOWN else None
        
        # Save JSON
        json_path = os.path.join(self.output_dir, json_name)
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(messages, jf, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON: {json_name}")
        
        # Save text
        txt_path = os.path.join(self.output_dir, txt_name)
        with open(txt_path, "w", encoding="utf-8") as tf:
            for msg in reversed(messages):
                tf.write(self.format_message_text(msg, format_type="text") + "\n")
                
                # Write thread replies with indentation
                if msg.get("thread_messages"):
                    tf.write(f"  ↳ Thread ({len(msg['thread_messages'])} replies):\n")
                    for reply in msg["thread_messages"]:
                        tf.write(self.format_message_text(reply, indent=2, format_type="text") + "\n")
                
                tf.write("\n")
        logger.info(f"Saved TXT: {txt_name}")
        
        # Save markdown if enabled
        if CREATE_MARKDOWN:
            md_path = os.path.join(self.output_dir, md_name)
            with open(md_path, "w", encoding="utf-8") as mf:
                mf.write(f"# Channel: #{cname}\n\n")
                mf.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                mf.write("---\n\n")
                
                for msg in reversed(messages):
                    mf.write(self.format_message_text(msg, format_type="markdown"))
                    
                    if msg.get("thread_messages"):
                        mf.write(f"  *↳ Thread ({len(msg['thread_messages'])} replies):*\n\n")
                        for reply in msg["thread_messages"]:
                            mf.write(self.format_message_text(reply, indent=2, format_type="markdown"))
                    
                    mf.write("\n")
            logger.info(f"Saved MD: {md_name}")
        
        files_created = f"{json_name}, {txt_name}"
        if CREATE_MARKDOWN:
            files_created += f", {md_name}"
        
        print(f"   ✅ Saved {files_created}")
        return (cname, msg_count, json_name, txt_name, md_name)


def main():
    """Main execution function."""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Slack Channel Export Tool - Starting")
    logger.info("=" * 60)
    
    try:
        exporter = SlackExporter(SLACK_TOKEN, OUTPUT_DIR)
        exporter.load_users()
        
        # Get and display channels (alphabetically sorted)
        channels = exporter.get_channels()
        logger.info(f"Found {len(channels)} accessible channels")
        print("\n📋 Channels available (alphabetical):")
        for i, c in enumerate(channels, start=1):
            privacy = "🔒" if c.get("is_private") else "🌐"
            print(f"{i:3}. {privacy} {c['name']}")
        
        # Channel selection
        sel = input("\nEnter channel number(s) (comma-separated, or 'all'): ").strip().lower()
        if sel == "all":
            selected = channels
            logger.info("User selected: ALL channels")
        else:
            try:
                selected = [channels[int(s)-1] for s in sel.split(",") if s.strip().isdigit()]
                logger.info(f"User selected {len(selected)} channel(s): {[c['name'] for c in selected]}")
            except Exception:
                logger.error("Invalid channel selection")
                raise SystemExit("❌ Invalid selection.")
        
        if not selected:
            logger.error("No channels selected")
            raise SystemExit("❌ No valid channels selected.")
        
        # Date range filter
        print("\n🕓 Select export window:")
        print("1. Last 7 days")
        print("2. Last 30 days")
        print("3. Last 60 days")
        print("4. Last 90 days")
        print("5. All messages (no filter)")
        choice = input("Enter selection [1-5]: ").strip()
        
        days_map = {"1": 7, "2": 30, "3": 60, "4": 90}
        days = days_map.get(choice)
        if days:
            cutoff_ts = time.mktime((datetime.now() - timedelta(days=days)).timetuple())
            print(f"⏱ Exporting messages newer than {days} days ago.\n")
            logger.info(f"Date filter: Last {days} days")
        else:
            cutoff_ts = None
            print("📜 Exporting all available messages.\n")
            logger.info("Date filter: ALL messages")
        
        print(f"Files will be created in:\n📂 {OUTPUT_DIR}\n")
        
        if DOWNLOAD_FILES:
            print("📥 File downloads enabled - this may take longer\n")
            logger.info("File downloads: ENABLED")
        
        # Create timestamp for filenames (YYYY-MM-DD-HHMM format)
        timestamp_str = datetime.now().strftime("%Y-%m-%d-%H%M")
        
        # Export channels
        summary = []
        skipped = []
        
        for ch in selected:
            try:
                result = exporter.export_channel(ch, cutoff_ts, timestamp_str)
                if result[1] == 0:  # No messages
                    skipped.append(result[0])
                else:
                    summary.append(result)
            except Exception as e:
                error_msg = f"Error exporting #{ch['name']}: {e}"
                print(f"❌ {error_msg}")
                logger.error(error_msg, exc_info=True)
                continue
        
        # Summary table
        if summary or skipped:
            print("\n🧾 EXPORT SUMMARY")
            print("─" * 100)
            print(f"{'Channel':<25} {'Messages':<10} {'Files Created':<60}")
            print("─" * 100)
            
            for cname, count, jfile, tfile, mfile in summary:
                files = f"{jfile}, {tfile}"
                if mfile:
                    files += f", {mfile}"
                print(f"{cname:<25} {count:<10} {files:<60}")
            
            if skipped:
                print("\n⚠️  Channels with no messages in date range (files not created):")
                for cname in skipped:
                    print(f"   • {cname}")
                logger.info(f"Skipped {len(skipped)} empty channels: {skipped}")
            
            print("─" * 100)
            print(f"🎯 Files saved to: {OUTPUT_DIR}\n")
            
            if DOWNLOAD_FILES:
                attach_dir = os.path.join(OUTPUT_DIR, "attachments")
                if os.path.exists(attach_dir):
                    print(f"📥 Attachments saved to: {attach_dir}\n")
            
            # Save anonymization key
            key_file = os.path.join(OUTPUT_DIR, f"{timestamp_str}-anonymization-key.json")
            anon_key = {anon: exporter.id_to_name.get(uid, uid) for uid, anon in exporter.anon_map.items()}
            with open(key_file, "w", encoding="utf-8") as kf:
                json.dump(anon_key, kf, indent=2)
            print(f"🔑 Anonymization key saved to: {os.path.basename(key_file)}")
            print("    (Keep this file secure - it maps anonymous IDs back to real usernames)\n")
            logger.info(f"Saved anonymization key: {key_file}")
            
            # Export statistics
            total_messages = sum(s[1] for s in summary)
            elapsed_time = datetime.now() - start_time
            print(f"📊 Export Statistics:")
            print(f"   • Channels exported: {len(summary)}")
            print(f"   • Total messages: {total_messages}")
            print(f"   • Time elapsed: {elapsed_time.total_seconds():.1f} seconds")
            
            if ENABLE_LOGGING:
                log_file = os.path.join(OUTPUT_DIR, f"slack_export_{start_time.strftime('%Y%m%d_%H%M%S')}.log")
                print(f"   • Log file: {os.path.basename(log_file)}")
            
            logger.info("=" * 60)
            logger.info(f"Export completed successfully")
            logger.info(f"Channels: {len(summary)}, Messages: {total_messages}, Time: {elapsed_time.total_seconds():.1f}s")
            logger.info("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Export interrupted by user")
        logger.warning("Export interrupted by user (KeyboardInterrupt)")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Fatal error: {e}"
        print(f"\n❌ {error_msg}")
        logger.error(error_msg, exc_info=True)
        sys.exit(1)
    finally:
        # Pause before closing (Windows convenience)
        print("\n" + "─" * 60)
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
