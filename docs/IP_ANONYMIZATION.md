IP Address Anonymization Feature
Overview
The IP anonymization feature helps protect privacy by replacing public IP addresses with [IP-REDACTED] while keeping private/internal IP addresses intact. This is especially useful for TAK (Team Awareness Kit) and other networking discussions where configs are shared.

Why This Matters
Public IPs are sensitive because they can reveal:

Geographic location
Organization/ISP
Network infrastructure details
Potential security vulnerabilities
Private IPs are safe because they:

Only work within local networks
Are meaningless outside your environment
Don't reveal location or organization
Are reused by millions of networks
What Gets Anonymized
✅ Public IPs (Replaced with [IP-REDACTED])
Any routable internet IP address:

Before: "Server at 203.0.113.45 is responding"
After:  "Server at [IP-REDACTED] is responding"

Before: "Connect to 198.51.100.10:8080"
After:  "Connect to [IP-REDACTED]:8080"

Before: "NAT from 203.0.113.45 to 10.1.1.5"
After:  "NAT from [IP-REDACTED] to 10.1.1.5"
❌ Private/Internal IPs (KEPT as-is)
RFC 1918 Private Ranges:

10.0.0.0/8 → All 10.x.x.x addresses
172.16.0.0/12 → 172.16.x.x through 172.31.x.x
192.168.0.0/16 → All 192.168.x.x addresses
Special Use:

127.0.0.0/8 → Localhost (127.0.0.1, etc.)
169.254.0.0/16 → Link-local addresses
0.0.0.0 → Unspecified address
Public DNS Servers (commonly referenced, not sensitive):

8.8.8.8, 8.8.4.4 (Google DNS)
1.1.1.1, 1.0.0.1 (Cloudflare DNS)
9.9.9.9 (Quad9)
208.67.222.222, 208.67.220.220 (OpenDNS)
Examples
✅ KEPT: "TAK Server at 10.5.10.20"
✅ KEPT: "Gateway is 192.168.1.1"
✅ KEPT: "Use DNS 8.8.8.8"
✅ KEPT: "Localhost 127.0.0.1 is fine"

❌ REDACTED: "Public server 203.0.113.45"
❌ REDACTED: "Connect to 198.51.100.10"
❌ REDACTED: "WAN IP: 151.101.1.69"
Configuration
Enable in config.json
json
{
  "features": {
    "anonymize_ips": true
  }
}
Default Setting
Disabled by default to avoid unexpected changes to your exports. Enable it when:

Sharing exports publicly
Posting to forums/GitHub
Compliance requires IP redaction
Working with sensitive network configs
Real-World TAK Examples
Network Configuration Discussion
Original:

My TAK server is at 203.0.113.45:8089 (WAN) 
and 10.5.10.20:8089 (LAN). 

Clients connect via:
- Local: 10.5.10.20
- Remote: 203.0.113.45

DNS: 8.8.8.8
Gateway: 192.168.1.1
Anonymized:

My TAK server is at [IP-REDACTED]:8089 (WAN) 
and 10.5.10.20:8089 (LAN). 

Clients connect via:
- Local: 10.5.10.20
- Remote: [IP-REDACTED]

DNS: 8.8.8.8
Gateway: 192.168.1.1
Result: Your public IP is protected, but the useful internal network details remain for troubleshooting.

Firewall Rule Example
Original:

Allow 203.0.113.45 → 10.5.10.20:8089
Allow 10.5.10.0/24 → 10.5.10.20:8089
Allow ANY → 203.0.113.45:443
Anonymized:

Allow [IP-REDACTED] → 10.5.10.20:8089
Allow 10.5.10.0/24 → 10.5.10.20:8089
Allow ANY → [IP-REDACTED]:443
VPN Configuration
Original:

OpenVPN server: 203.0.113.45:1194
Local subnet: 10.8.0.0/24
Client IP: 10.8.0.2
Anonymized:

OpenVPN server: [IP-REDACTED]:1194
Local subnet: 10.8.0.0/24
Client IP: 10.8.0.2
Technical Details
IPv4 Pattern Matching
The feature uses regex to identify IPv4 addresses:

regex
\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b
Matches valid IPv4 addresses like:

✅ 192.168.1.1
✅ 10.0.0.1
✅ 203.0.113.45
❌ 999.999.999.999 (invalid)
❌ 1.2.3 (incomplete)
Classification Logic
python
1. Extract all IP addresses from text
2. For each IP:
   a. Check if private (10.x, 192.168.x, 172.16-31.x)
   b. Check if special use (127.x, 169.254.x, 0.0.0.0)
   c. Check if common public DNS
   d. If any above → KEEP
   e. Otherwise → REPLACE with [IP-REDACTED]
IPv6 Support
Currently: IPv6 addresses are NOT anonymized.

Reason: IPv6 anonymization is more complex due to:

Different notation (::1, 2001:db8::1, etc.)
Privacy extensions already built into IPv6
Less common in TAK deployments
Future: Could be added if there's demand. Let us know if you need IPv6 anonymization!

Limitations
What This Doesn't Protect
Hostnames/Domains
   "Connect to takserver.example.com" → NOT anonymized
Hostnames may still reveal information. Consider anonymizing these separately if needed.

Ports
   "Server on 203.0.113.45:8089" → "[IP-REDACTED]:8089"
Ports remain visible. Non-standard ports could reveal service types.

Network Context
   "My home server at 203.0.113.45"
Even redacted, the context reveals it's a home server.

IPs in Code Blocks
   "Here's my config:
```yaml
   server_ip: 203.0.113.45
```
IPs in code blocks ARE anonymized, but complex configs may need manual review.

IP Fragments
   "First 3 octets: 203.0.113"
Partial IPs don't match the pattern and won't be redacted.

Best Practices
When to Enable
✅ Enable when:

Sharing exports on public forums
Posting troubleshooting logs
Contributing to open-source discussions
Compliance requires IP redaction
Unsure about sensitivity
❌ Keep disabled when:

Exports are for internal use only
You control all recipients
IPs are needed for troubleshooting
Already behind secure channels
Additional Privacy Steps
Even with IP anonymization enabled, consider:

Review exports before sharing
Check for other sensitive data (keys, passwords, hostnames)
Verify redaction worked as expected
Anonymize hostnames if needed
Replace mycompany.com with [DOMAIN-REDACTED]
Edit manually or add custom rules
Remove credential references
API keys, tokens, passwords
Even if hashed/partial
Consider context
"My home lab at [IP-REDACTED]" still reveals it's a home lab
Rephrase sensitive context before sharing
Testing
Verify It's Working
Enable in config:
json
   "anonymize_ips": true
Export a channel with IP addresses
Check the text output:
   Public IPs should show: [IP-REDACTED]
   Private IPs should show: 10.x.x.x, 192.168.x.x, etc.
Grep for public IPs in your export:
bash
   # Should find none (or only private IPs)
   grep -E '\b[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b' export.txt
Test Cases
Create a test message with various IPs:

Public: 203.0.113.45, 198.51.100.10
Private: 10.1.1.5, 192.168.1.1, 172.16.0.1
Special: 127.0.0.1, 0.0.0.0, 169.254.1.1
DNS: 8.8.8.8, 1.1.1.1
Expected output:

Public: [IP-REDACTED], [IP-REDACTED]
Private: 10.1.1.5, 192.168.1.1, 172.16.0.1
Special: 127.0.0.1, 0.0.0.0, 169.254.1.1
DNS: 8.8.8.8, 1.1.1.1
Troubleshooting
IPs Not Being Redacted
Check:

anonymize_ips: true in config.json?
IP is actually public (not in private ranges)?
IP format is valid (xxx.xxx.xxx.xxx)?
Private IPs Being Redacted
Should not happen, but if it does:

Check IP is in valid private range
Report as a bug with example IP
False Positives
If a number sequence looks like an IP but isn't:

"Version 10.5.10.20 released" → Might get anonymized
This is rare but possible. Manual review catches these.

Performance Impact
Minimal - IP anonymization adds ~1ms per message due to regex matching. Even with thousands of messages, the impact is negligible compared to network I/O for downloads.

Privacy Considerations
What This Achieves
✅ Hides your public internet presence
✅ Protects network infrastructure details
✅ Prevents geographic tracking
✅ Maintains useful internal network info

What This Doesn't Achieve
❌ Doesn't protect usernames (see anonymization key)
❌ Doesn't redact hostnames/domains
❌ Doesn't remove all context clues
❌ Doesn't replace manual security review

Bottom line: IP anonymization is ONE layer of privacy protection. Always review exports before sharing sensitive data publicly.

Feedback
This feature was designed for the TAK community's needs. If you have suggestions:

Need IPv6 support?
Want hostname anonymization?
Other network identifiers to redact?
Open an issue on GitHub or submit feedback!

Version: 2.1
Last Updated: October 2025
License: MIT

