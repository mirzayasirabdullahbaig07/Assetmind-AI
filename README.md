<p align="center">
  <img src="docs/banner.svg" alt="AssetMind Banner" width="100%">
</p>

<h1 align="center">🧠 AssetMind</h1>
<p align="center"><b>Smart Office Asset Memory & Maintenance System</b><br>Built for Nexora Technologies</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-2563EB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/SQLite-Database-14B8A6?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Groq-AI%20Powered-8B5CF6?style=for-the-badge" alt="Groq AI">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Hackathon%20Prototype-F59E0B?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-64748B?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Assets%20Tracked-280-2563EB?style=flat-square" alt="Assets">
  <img src="https://img.shields.io/badge/Made%20with-Plotly%20%7C%20OpenCV%20%7C%20ReportLab-0EA5E9?style=flat-square" alt="Stack">
</p>

<p align="center">
  <i>Physical object → Digital identity → Visual evidence → Condition → Maintenance → Repair → Replacement → Historical memory</i>
</p>

---

## 📖 About

**AssetMind** is a digital memory and lifecycle system for physical office assets — not just an
inventory tracker. Every asset at the fictional software house **Nexora Technologies** (desktops,
laptops, chairs, monitors, and more) gets a permanent digital identity that remembers everything
that ever happens to it: assignment, maintenance, AI-assisted inspection, repair, and replacement.

Nothing is ever deleted. A retired asset stays in the database forever, linked to whatever replaced it.

## ✨ Features

| Category | What it does |
|---|---|
| 🏠 **Dashboard** | Live metrics and Plotly charts — status, type, and department breakdowns |
| 📦 **Assets** | Search, filter, and open a full asset profile with a database-backed history timeline |
| 🔧 **Maintenance** | Report issues → ticket workflow → repair or replacement, fully status-tracked |
| 📸 **AI Inspection** | Groq vision model analyzes photos for *visible* condition only — never claims hidden/internal faults |
| 🤖 **Ask AssetMind** | Natural-language Q&A, answered only from real SQLite results via safe, predefined functions |
| 📊 **Reports** | Monthly maintenance reports with CSV and PDF export |
| 🏷️ **QR Assets** | Generate, download, and look up any asset by QR code or manual ID |
| ⚙️ **Settings** | API key status, database info, and confirmed demo data reset |

## 🛠️ Tech Stack

- **App framework:** Streamlit (single app — no separate frontend/backend)
- **Language:** Python
- **Database:** SQLite via SQLAlchemy
- **AI:** Groq API — text model for reasoning, vision model for image inspection
- **Charts:** Plotly
- **QR codes:** `qrcode`
- **Image handling:** OpenCV, Pillow
- **PDF reports:** ReportLab

## 🚀 Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd assetmind

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Groq API key
copy .env.example .env       # Windows
cp .env.example .env         # macOS/Linux
# then edit .env and paste your key from console.groq.com

# 5. Run
streamlit run app.py
```

The database (`assetmind.db`) and ~280 synthetic Nexora Technologies assets are created
automatically on first run — restarting never duplicates data.

## 📂 Project Structure

```
assetmind/
├── app.py                  # Entry point / landing page
├── pages/                  # Streamlit multipage sections (Dashboard, Assets, ...)
├── database/                # SQLite schema, connection, seed data
├── ai/                      # Groq client, vision inspection, assistant routing, prompts
├── services/                # Business logic — assets, maintenance, history, reports, QR
├── components/              # Reusable UI pieces — charts, timeline, status badges
├── utils/                   # Validators, helpers, PDF export
├── uploads/                 # Asset, inspection, repair, and QR images (local storage)
├── docs/banner.svg          # README banner
└── .streamlit/config.toml   # Theme
```

## ⚠️ Known Limitations (by design)

- **Local storage:** `uploads/` and `assetmind.db` are ephemeral on Streamlit Community Cloud
  (reset on redeploy/sleep). The storage layer is modular so it can be swapped for cloud storage later.
- **AI is decision support, not diagnosis.** The vision model reports only what's visually
  evident and explicitly defers to manual inspection when evidence is insufficient — this is a
  safety feature, not a gap to close.
- **Synthetic data:** most of the 280 assets are generated demo records. A handful of real physical
  objects can be photographed for live AI Inspection demos.

## ☁️ Deployment — Streamlit Community Cloud

1. Push this repo to GitHub (`.env` is gitignored — never commit real keys).
2. Create a new app on [share.streamlit.io](https://share.streamlit.io) pointing to `app.py`.
3. In **Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_key_here"
   ```
4. Deploy — the database and demo data initialize automatically on first load.

## 🎬 Demo Flow (~3 minutes)

1. **Dashboard** — ~280 assets across Nexora Technologies
2. **Assets** — open a chair (e.g. `C-018`), show its history
3. **Maintenance** — report an issue with a photo
4. **AI Inspection** — Groq vision analyzes it, flags manual inspection where needed
5. Move the ticket: Reviewing → Replacement Requested → **Retire** the asset
6. **Create its replacement** — linked in the database, old asset preserved forever
7. **Ask AssetMind** — *"Which assets need attention?"* and *"Which assets were repaired more than twice?"*
8. **Reports** — generate and export the monthly maintenance report

---

<p align="center"><sub>Built as a hackathon prototype. Not a production-ready enterprise system.</sub></p>
