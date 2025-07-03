from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

SYMBOL = "AVAXUSDT"
LEVERAGE = 5
FIXED_QUANTITY = 10  # 10 adet AVAX

client = Client(API_KEY, API_SECRET)
client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)

app = Flask(__name__)

def get_position():
    positions = client.futures_position_information(symbol=SYMBOL)
    for pos in positions:
        amt = float(pos['positionAmt'])
        if amt != 0:
            return amt
    return 0

def close_open_position():
    amt = get_position()
    if amt > 0:
        client.futures_create_order(symbol=SYMBOL, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=abs(amt))
        print("LONG pozisyon kapatıldı")
    elif amt < 0:
        client.futures_create_order(symbol=SYMBOL, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=abs(amt))
        print("SHORT pozisyon kapatıldı")

def calculate_quantity():
    return str(round(FIXED_QUANTITY, 2))

@app.route("/")
def home():
    return "NRTR Binance Bot çalışıyor.", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(f"Webhook alındı: {data}")

    signal = data.get("side")
    if signal not in ["buy", "sell"]:
        return "Geçersiz sinyal", 400

    close_open_position()
    qty = calculate_quantity()

    if float(qty) <= 0:
        return "Miktar geçersiz, işlem yapılmadı.", 400

    if signal == "buy":
        client.futures_create_order(symbol=SYMBOL, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=qty)
        print(f"LONG açıldı: {qty} AVAX")
    elif signal == "sell":
        client.futures_create_order(symbol=SYMBOL, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=qty)
        print(f"SHORT açıldı: {qty} AVAX")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
