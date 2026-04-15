# Zircon FRT — User Guide

## Overview

Zircon FRT (Forensic Research Tool) is an OSINT data collection and analysis platform. It enables analysts to upload documents, search their contents with full-text search, monitor brands for typosquatting, and track suspicious indicators.

---

## Getting Started

### Logging In

1. Navigate to your Zircon FRT instance URL
2. Enter your **email** and **password**
3. Click **Sign In**

To register a new account, click **Create account** on the login page.

---

## Dashboard

The Dashboard provides an at-a-glance summary:

| Metric | Description |
|--------|-------------|
| Total Files | All uploaded files in the system |
| Indexed Files | Files successfully indexed and searchable |
| Alerts Today | Brand protection and monitoring alerts in the last 24h |
| Active Monitors | Currently active watchlist monitors |

---

## Uploading Files

1. Navigate to **Files** in the sidebar
2. Click **Upload File** or drag and drop a file into the upload zone
3. Supported formats: `.txt`, `.log`, `.md`, `.csv`, `.json`, `.sql`, `.pdf`, `.docx`, `.doc`, `.xlsx`, `.xls`, `.xml`
4. After upload, the file is queued for indexing
5. Once indexed, it becomes searchable

### File Management

- **View**: Click a file row to see its metadata and extracted text preview
- **Download**: Click the download icon to retrieve the original file
- **Delete**: Click the trash icon to permanently remove a file

---

## Searching Files

1. Navigate to **Search** in the sidebar
2. Enter your query in the search bar
3. Use **filters** on the left to narrow by file type or date range
4. Results are ranked by relevance with highlighted snippets

### Search Syntax

| Syntax | Example | Description |
|--------|---------|-------------|
| Plain text | `malware report` | Match any of the words |
| Exact phrase | `"command and control"` | Match exact phrase |
| AND | `phishing AND credential` | Both terms must appear |
| OR | `ransomware OR wiper` | Either term |
| NOT | `report NOT summary` | Exclude term |
| Wildcard | `pass*` | Prefix wildcard |

### Exporting Search Results

After performing a search, click the export buttons that appear above the results:

- **Export CSV** — comma-separated file with file IDs, names, types, scores
- **Export JSON** — structured JSON with all result metadata
- **Export PDF** — formatted PDF report

---

## Brand Protection

The Brand Protection module monitors for typosquatting and phishing domains mimicking your brand.

### Adding a Brand Watch

1. Navigate to **Brand Protection**
2. Click **Add Brand**
3. Fill in:
   - **Brand Name**: Display name (e.g., "Acme Corp")
   - **Original URL**: Your official domain (e.g., `https://acme.com`)
   - **Keywords**: Comma-separated terms to monitor
   - **Similarity Threshold**: Minimum similarity % to generate an alert (default: 70%)
   - **Scan Schedule**: Hourly, Daily, or Weekly
4. Click **Add Brand**

### Viewing Alerts

1. Click **View Details** on a brand card
2. The alerts table shows:
   - **Found Domain**: The suspicious domain detected
   - **Similarity**: How closely it resembles your brand (circular gauge)
   - **Detection Sources**: DNS, WHOIS, SSL, search engines
   - **Status**: New / Reviewed / Dismissed
3. Actions:
   - **Reviewed**: Mark an alert as investigated
   - **Dismiss**: Ignore a false positive
   - **Reopen**: Re-flag a dismissed alert

### Triggering a Manual Scan

Click **Deep Scan** in the detail view to run an immediate scan outside the schedule.

### Exporting Brand Alerts

In the brand detail view, click the export buttons when alerts are present:

- **Export CSV**, **Export JSON**, or **Export PDF**

---

## Monitoring (Watchlist)

Track specific indicators: IP addresses, domains, email addresses, hashes.

### Adding a Watchlist Item

1. Navigate to **Monitoring**
2. Click **Add Item**
3. Select the **type**: IP, Domain, Email, Hash, Keyword
4. Enter the **value**
5. Choose a **check interval**
6. Click **Save**

When a monitored item generates an event (e.g., a domain changes IP, or appears in threat feeds), an alert is created and shown in the events list.

### Exporting the Watchlist

Go to **Monitoring** and use the export button to download your watchlist as CSV or JSON.

---

## Notifications

Real-time notifications appear in the bell icon (top right). They are also pushed via WebSocket for instant delivery.

- Click the bell to view all notifications
- Click **Mark all as read** to clear the badge

---

## Settings

### Profile

- Update your display name and email
- Change your password

### Integrations

Connect external services:

- **Email**: Configure SMTP for email notifications
- **Webhook**: Receive HTTP POST notifications to a custom URL
- **Telegram**: Bot token + chat ID for Telegram alerts

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Focus search bar |
| `Esc` | Close modal |

---

## Troubleshooting

**Search returns no results**
- Ensure the file has been indexed (check the Files page — indexed files show a green indicator)
- Try a simpler query

**Brand scan shows no alerts**
- The similarity threshold may be too high — try lowering it to 60%
- Run a manual **Deep Scan** to check immediately

**File upload fails**
- Maximum file size is configured by your administrator (default: 100 MB)
- Ensure the file format is supported
