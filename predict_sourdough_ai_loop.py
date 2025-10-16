from flask import Flask
import threading
import time
import pandas as pd
import joblib
import requests

# ====== CONFIGURATION ======
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1rpLN-HQcbzrq2kkumDnHU7OhH0LUSRJx5AtRcm5coFs/export?format=csv"
MODEL_PATH = "sourdough_feeding_model.joblib"
BOT_TOKEN = "7695970307:AAG18bE_Wq5pjxeUjpEPJwQ2nv7EdCCgS2s"
CHAT_ID = "1121168320"
# ===========================

app = Flask(__name__)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.get(url, params=params, timeout=10)
    except Exception as e:
        print("❌ Telegram error:", e)

def ai_loop():
    while True:
        try:
            df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
            df.columns = df.columns.str.lower()
            latest = df.iloc[-1]
            X = [[float(latest["co2"]), float(latest["temperature"]), float(latest["humidity"]), float(latest["distance"])]]
            model = joblib.load(MODEL_PATH)
            prediction = model.predict(X)[0]

            if prediction == 1:
                msg = "🍞 Feed your starter now!"
                print(msg)
                send_telegram_message(msg)
            else:
                print("⏳ Not feeding time yet.")

        except Exception as e:
            print("⚠️ Error during prediction:", e)

        time.sleep(180)  # wait 3 minutes

@app.route("/")
def home():
    return "Sourdough AI Bot is running!"

# Start AI loop in background thread
threading.Thread(target=ai_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
