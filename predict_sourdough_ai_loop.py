import pandas as pd
import joblib
import requests
import time
from flask import Flask
import threading

# ====== CONFIGURATION ======
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1rpLN-HQcbzrq2kkumDnHU7OhH0LUSRJx5AtRcm5coFs/export?format=csv"
MODEL_PATH = "sourdough_feeding_model.joblib"
BOT_TOKEN = "7695970307:AAG18bE_Wq5pjxeUjpEPJwQ2nv7EdCCgS2s"
CHAT_ID = "1121168320"
CHECK_INTERVAL = 60 * 3   # every 3 minutes
# ============================

def send_telegram_message(text):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.get(url, params=params, timeout=10)
        print("✅ Telegram message sent!")
    except Exception as e:
        print("❌ Telegram send failed:", e)

def main():
    print("🤖 Loading AI model...")
    model = joblib.load(MODEL_PATH)
    last_feed_status = None  # To avoid duplicate notifications

    app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Sourdough AI Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web, daemon=True).start()

    while True:
        try:
            print("\n📡 Checking Google Sheet...")
            df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
            df.columns = df.columns.str.lower()

            # Extract latest reading
            latest = df.iloc[-1]
            X = [[float(latest["co2"]), float(latest["temperature"]),
                  float(latest["humidity"]), float(latest["distance"])]]

            # Predict feeding time
            prediction = model.predict(X)
            feed_now = int(prediction[0])

            # Check and send notification only if feed_now changes
            if feed_now != last_feed_status:
                last_feed_status = feed_now
                if feed_now == 1:
                    msg = "🍞 It's time to FEED your sourdough starter!"
                else:
                    msg = "⏳ Starter is still fermenting, not feeding time yet."
                print(msg)
                send_telegram_message(msg)
            else:
                print("No change since last check.")

        except Exception as e:
            print("⚠️ Error during check:", e)

        print(f"Sleeping for {CHECK_INTERVAL/60:.0f} minutes...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

