# slack_channel_export_tool.py
from slack_sdk import WebClient
import json, re, os, time
from datetime import datetime, timedelta

# === USER SETTINGS ===
SLACK_TOKEN = "xoxp-123456789..."        # Paste your Slack user token here
OUTPUT_DIR = r"C:\SlackExports\Output"              # Folder to save output files (edit as needed)
# ======================

client = WebClient(token=SLACK_TOKEN)
os.makedirs(OUTPUT_DIR, exist_ok=True)
date_str = datetime.now().strftime("%Y-%m-%d")

print("\n🔗 Connecting to Slack workspace...")

# --- Load users ---
users, cursor = [], None
while True:
    resp = client.users_list(cursor=cursor)
    users.extend(resp["members"])
    cursor = resp.get("response_metadata", {}).get("next_cursor")
    if not cursor:
        break

id_to_name = {u["id"]: u.get("profile", {}).get("display_name") or u.get("name") for u in users}
print(f"👥 Loaded {len(id_to_name)} user profiles")

# --- Get channel list ---
channels, cursor = [], None
while True:
    resp = client.conversations_list(types="public_channel,private_channel", cursor=cursor, limit=200)
    channels.extend(resp["channels"])
    cursor = resp.get("response_metadata", {}).get("next_cursor")
    if not cursor:
        break

if not channels:
    raise SystemExit("❌ No channels found or token missing proper read scopes.")

print("\n📋 Numbered list of available channels:")
for i, c in enumerate(channels, start=1):
    print(f"{i:3}. {c['name']}")

# --- Channel selection ---
sel = input("\nEnter channel number(s) (comma-separated): ").strip()
try:
    selected = [channels[int(s)-1] for s in sel.split(",") if s.strip().isdigit()]
except Exception:
    raise SystemExit("❌ Invalid selection.")

if not selected:
    raise SystemExit("❌ No valid channels selected.")

multi_choice = input("\nWould you like separate files for each channel? [y/n]: ").lower().startswith("y")

# --- Date range filter ---
print("\n🕓 Select export window:")
print("1. Last 30 days")
print("2. Last 60 days")
print("3. Last 90 days")
print("4. All messages (no filter)")
choice = input("Enter selection [1-4]: ").strip()

days_map = {"1": 30, "2": 60, "3": 90}
days = days_map.get(choice)
if days:
    cutoff_ts = time.mktime((datetime.now() - timedelta(days=days)).timetuple())
    print(f"⏱ Exporting messages newer than {days} days ago.\n")
else:
    cutoff_ts = None
    print("📜 Exporting all available messages.\n")

print(f"The following file(s) will be created in:\n📂 {OUTPUT_DIR}\n")

# --- Helper functions ---
anon_map = {}
anon_counter = 1
def anon_id(uid):
    global anon_counter
    if uid not in anon_map:
        anon_map[uid] = f"anon{anon_counter:02d}"
        anon_counter += 1
    return anon_map[uid]

def clean_text(t):
    t = re.sub(r"<@U[0-9A-Z]+>", lambda m: f"[{anon_id(m.group(0))}]", t)
    t = re.sub(r":\w+:", "", t)
    t = re.sub(r"<(http[^>]+)>", r"\1", t)
    return t.strip()

# --- Export & sanitize ---
summary = []
combined_json, combined_txt = [], []

for ch in selected:
    cname = ch["name"]
    print(f"📡 Exporting channel: #{cname}")

    messages, cursor = [], None
    while True:
        resp = client.conversations_history(channel=ch["id"], cursor=cursor, limit=200)
        batch = resp["messages"]
        if cutoff_ts:
            batch = [m for m in batch if float(m["ts"]) >= cutoff_ts]
        messages.extend(batch)
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    msg_count = len(messages)
    print(f"   → Retrieved {msg_count} messages")

    json_name = f"{date_str}-Slack-TAK_USERS-{cname}.json"
    txt_name = f"{date_str}-Slack-TAK_USERS-{cname}.txt"

    # Save JSON
    with open(os.path.join(OUTPUT_DIR, json_name), "w", encoding="utf-8") as jf:
        json.dump(messages, jf, indent=2, ensure_ascii=False)

    # Save text
    with open(os.path.join(OUTPUT_DIR, txt_name), "w", encoding="utf-8") as tf:
        for msg in reversed(messages):
            uid = msg.get("user", "")
            anon = anon_id(uid)
            text = clean_text(msg.get("text", ""))
            tf.write(f"{anon}: {text}\n")

    print(f"   ✅ Saved {json_name} and {txt_name}")
    summary.append((cname, msg_count, json_name, txt_name))

    # Combine outputs if desired
    if not multi_choice and len(selected) > 1:
        combined_json.append({cname: messages})
        combined_txt.append(f"\n--- #{cname} ---\n")
        for msg in reversed(messages):
            uid = msg.get("user", "")
            anon = anon_id(uid)
            text = clean_text(msg.get("text", ""))
            combined_txt.append(f"{anon}: {text}\n")

# --- Write combined files ---
if not multi_choice and len(selected) > 1:
    cj_name = f"{date_str}-Slack-TAK_USERS-Combined.json"
    ct_name = f"{date_str}-Slack-TAK_USERS-Combined.txt"
    with open(os.path.join(OUTPUT_DIR, cj_name), "w", encoding="utf-8") as jf:
        json.dump(combined_json, jf, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTPUT_DIR, ct_name), "w", encoding="utf-8") as tf:
        tf.writelines(combined_txt)
    print(f"\n📦 Combined output saved as {cj_name} and {ct_name}")
    summary.append(("Combined", sum([s[1] for s in summary]), cj_name, ct_name))

# --- Summary table ---
print("\n🧾 EXPORT SUMMARY")
print("─" * 90)
print(f"{'Channel':<25} {'Messages':<10} {'JSON File':<30} {'TXT File':<30}")
print("─" * 90)
for cname, count, jfile, tfile in summary:
    print(f"{cname:<25} {count:<10} {jfile:<30} {tfile:<30}")
print("─" * 90)
print(f"🎯 Files saved to: {OUTPUT_DIR}\n")
