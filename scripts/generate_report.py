# Load local .env file for development only (ignored in production)
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime

import requests
import yfinance as yf
import os
import shutil
import pytz

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# ---------------------- DATA FETCHING FUNCTIONS ----------------------
def get_exchange_rates():
    url = "https://api.frankfurter.app/latest"
    params = {"symbols": "USD,DKK,GBP,SEK"}

    response = requests.get(url, params=params)
    data = response.json()

    rates = data.get("rates", {})
    eur_to_usd = rates.get("USD")
    eur_to_dkk = rates.get("DKK")
    eur_to_gbp = rates.get("GBP")
    eur_to_sek = rates.get("SEK")

    if eur_to_usd and eur_to_dkk and eur_to_gbp and eur_to_sek:
        usd_to_dkk = eur_to_dkk / eur_to_usd
        usd_to_gbp = eur_to_gbp / eur_to_usd
        gbp_to_dkk = eur_to_dkk / eur_to_gbp
        sek_to_dkk = eur_to_dkk / eur_to_sek
        return usd_to_dkk, usd_to_gbp, gbp_to_dkk, sek_to_dkk
    else:
        raise Exception("Failed to get required exchange rates.")

def get_xau_xag_to_dkk():

    if TEST_MODE:
        print("⚠️ Skipping metal API in test mode.")
        return 20000, 200  # ← Dummy XAU and XAG values for testing

    api_key = os.getenv("METAL_API_KEY")
    if not api_key:
        print("❌ Missing METAL_API_KEY in environment.")
        return None, None

    url = "https://api.metalpriceapi.com/v1/latest"
    params = {
        "api_key": api_key,
        "base": "XAU",
        "currencies": "USD,DKK,XAG"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not data.get("success", False):
        return None, None

    rates = data.get("rates", {})
    xau_to_usd = rates.get("USD")
    xau_to_dkk = rates.get("DKK")
    xau_to_xag = rates.get("XAG")

    if xau_to_usd and xau_to_dkk and xau_to_xag:
        xag_to_dkk = xau_to_dkk / xau_to_xag
        return xau_to_dkk, xag_to_dkk
    else:
        return None, None

# Function no longer used, but kept for reference
def get_accenture_stock_price(usd_to_dkk):
    try:
        ticker = yf.Ticker("ACN")
        price_usd = ticker.info["regularMarketPrice"]
        price_dkk = price_usd * usd_to_dkk
        return price_usd, price_dkk
    except Exception:
        return None, None

def get_stock_price_yf(ticker_symbol, usd_to_dkk=None):
    try:
        ticker = yf.Ticker(ticker_symbol)
        price = ticker.info["regularMarketPrice"]
        if usd_to_dkk:
            return price, price * usd_to_dkk
        else:
            return price, None
    except Exception:
        return None, None

# Generate timestamp
cet = pytz.timezone("Europe/Copenhagen")
timestamp = datetime.now(cet).strftime("%Y-%m-%d %H:%M CET") # ← YYYY-MM-DD in CET

# ---------------------- HTML REPORT ----------------------
def build_report_table_html(usd_to_dkk, gbp_to_dkk, sek_to_dkk, xau_dkk, xag_dkk, acn_usd, acn_dkk, novo_dkk, green_dkk, timestamp):
    rows = f"""
        <tr><td>1 USD</td><td>{usd_to_dkk:.4f} DKK</td></tr>
        <tr><td>1 GBP</td><td>{gbp_to_dkk:.4f} DKK</td></tr>
        <tr><td>1 SEK</td><td>{sek_to_dkk:.4f} DKK</td></tr>
        <tr><td>1 XAU (Gold)</td><td>{f"{xau_dkk:.2f} DKK" if xau_dkk else "N/A"}</td></tr>
        <tr><td>1 XAG (Silver)</td><td>{f"{xag_dkk:.2f} DKK" if xag_dkk else "N/A"}</td></tr>
        <tr><td>Accenture (ACN)</td><td>{f"{acn_usd:.2f} USD / {acn_dkk:.2f} DKK" if acn_usd and acn_dkk else "N/A"}</td></tr>
        <tr><td>Novo Nordisk (NOVO-B.CO)</td><td>{f"{novo_dkk:.2f} DKK" if novo_dkk else "N/A"}</td></tr>
        <tr><td>GreenMobility (GREENM.CO)</td><td>{f"{green_dkk:.2f} DKK" if green_dkk else "N/A"}</td></tr>
    """

    html = f"""
    <html>
    <head>
        <title>Daily Currency & Market Update</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Favicons -->
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
        <link rel="manifest" href="/site.webmanifest">
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                padding: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
                font-size: 1rem;
            }}
            thead {{
                background-color: #f2f2f2;
            }}
            img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 20px auto;
            }}
            p {{
                font-size: 0.8rem;
                color: #999;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 style="text-align:center;">💱 Daily Currency & Market Update</h2>
            <table>
                <thead>
                    <tr><th>Asset</th><th>Value</th></tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
                <div style="
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 12px;
                margin-top: 24px;
            ">
            <button onclick="location.href='side-projects.html'" style="
                padding: 10px 16px;
                font-size: 16px;
                border-radius: 8px;
                border: none;
                background-color: #007aff;
                color: white;
                cursor: pointer;
                flex: 1 1 200px;
                max-width: 250px;
            ">
                🛠️ Side Projects
            </button>
            <button onclick="location.reload()" style="
                padding: 10px 16px;
                font-size: 16px;
                border-radius: 8px;
                border: none;
                background-color: #007aff;
                color: white;
                cursor: pointer;
                flex: 1 1 200px;
                max-width: 250px;
            ">
                🔄 Refresh
            </button>
            </div>


            <img src="./Logo_jfn_github.png" alt="Logo" style="margin-top: 20px;">
            <p>Generated on {timestamp} CET by GitHub Actions.</p>
            
        </div>
    </body>
    </html>
    """
    return html

# ---------------------- SAVE HTML AND LOGO ----------------------
def save_report_files(html_content, logo_path, output_dir="dist"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save HTML report
    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Saved HTML report to {html_path}")

    # Copy logo to output directory
    dest_logo_path = os.path.join(output_dir, "Logo_jfn_github.png")
    shutil.copyfile(logo_path, dest_logo_path)
    print(f"✅ Copied logo to {dest_logo_path}")

# ---------------------- MAIN EXECUTION ----------------------
if __name__ == "__main__":
    print("📡 Fetching market data...")

    usd_to_dkk, _, gbp_to_dkk, sek_to_dkk = get_exchange_rates()
    xau_dkk, xag_dkk = get_xau_xag_to_dkk()
    # acn_usd, acn_dkk = get_accenture_stock_price(usd_to_dkk)
    acn_usd, acn_dkk = get_stock_price_yf("ACN", usd_to_dkk)
    novo_dkk, _ = get_stock_price_yf("NOVO-B.CO")  # DKK native
    green_dkk, _ = get_stock_price_yf("GREENM.CO") # DKK native 


    # Generate HTML report
    html_output = build_report_table_html(usd_to_dkk, gbp_to_dkk, sek_to_dkk, xau_dkk, xag_dkk, acn_usd, acn_dkk, novo_dkk, green_dkk, timestamp)
    print("📧 Preview:\n", html_output)  # Optional for debugging

    # Save HTML and logo to dist/ directory
    save_report_files(html_output, "assets/Logo_jfn_github.png")