# 💱 Currency Report – Daily Static Web App

This project generates a daily currency and gold price report as a static HTML page using Python and GitHub Actions. The report is automatically deployed to Azure Static Web Apps and served via a custom domain.

---

## 📦 What's Included

### 🐍 scripts/generate_report.py

- Fetches real-time financial data (e.g., USD/DKK, gold prices)
- Builds a custom HTML report
- Saves the result to dist/index.html
- Embeds a local logo (Logo_jfn_github.png) into the final report

---

## ⚙️ GitHub Actions Workflows

Two GitHub workflows power the automation:

### 1. 🧾 generate-daily-report.yml

Generates the daily HTML report.

- Triggered every day at 05:00 UTC
- Runs the Python script to generate the report
- Commits the output to the dist/ folder

on:
  schedule:
    - cron: '0 5 * * *'
  workflow_dispatch:

### 2. 🚀 azure-static-web-apps.yml

Deploys the latest HTML report to Azure.

- Triggered every day at 06:00 UTC (after generation)
- Uses Azure deployment token authentication
- Uploads the dist/ folder to Azure Static Web Apps

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

---

## 🌐 Live Website

The latest report is always available at:

https://yellow-bush-02f213403.2.azurestaticapps.net
(or your custom domain, if configured)

---

## 🧪 Running Locally

Install dependencies:

pip install -r requirements.txt

Generate the report:

python scripts/generate_report.py

Open it locally:

open dist/index.html  # or use your browser

---

## 🛠 Requirements

- Python 3.10+
- Packages: requests, yfinance, pytz, python-dotenv
- GitHub Actions
- Azure Static Web App with deployment token

---

## 📁 Project Structure

.
├── dist/                         # Final HTML and assets
│   ├── index.html
│   └── Logo_jfn_github.png
├── scripts/
│   └── generate_report.py       # Python script to build the report
├── .github/
│   └── workflows/
│       ├── generate-daily-report.yml
│       └── azure-static-web-apps.yml
├── requirements.txt
└── README.md

---

## 📜 License

MIT — free to use, modify, and distribute.

---

## 🙌 Credits

Created and maintained by @norregaard
Financial data via public APIs and yfinance