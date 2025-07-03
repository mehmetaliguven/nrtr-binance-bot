from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os
import math

app = Flask(__name__)

# Binance API anahtarlarını ortam değişkenlerinden al
api_key = os.environ.get("BINANCE_API_KEY")
api_secret = os.environ.get("BINANCE_API_SECRET")

client = Client(api_key, api_secret)

SYMBOL = "AVAXUSDT"
QUANTITY = 10  # Sabit: 10 adet AVAX al/sat
TRAILING_STOP_PERCENT = 1.0  # %1 trailing stop
active_order = None
order_side = None
entry_price = None
highest_price = None

@app.route("/webhook", methods=["POST"])
def webhook():
    global active_order, order_side, entry_price, highest_price

    data = request.get_json()
    side = data.get("side", "").lower()

    if side not in ["buy", "sell"]:
        return "Invalid side", 400

    # Eğer açık bir pozisyon varsa önce kapat
    try:
        if active_order:
            close_side = SIDE_SELL if order_side == SIDE_BUY else SIDE_BUY
            client.futures_create_order(
                symbol=SYMBOL,
                side=close_side,
                type=ORDER_TYPE_MARKET,
                quantity=QUANTITY
            )
            active_order = None
            entry_price = None
            highest_price = None
            return "Previous position closed", 200
    except Exception as e:
        return f"Error closing previous order: {e}", 500

    # Yeni işlem aç
    try:
        response = client.futures_create_order(
            symbol=SYMBOL,
            side=SIDE_BUY if side == "buy" else SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=QUANTITY
        )
        active_order = response
        order_side = SIDE_BUY if side == "buy" else SIDE_SELL
        entry_price = float(response["avgFillPrice"]) if "avgFillPrice" in response else None
        highest_price = entry_price
        return f"{side.capitalize()} Order Executed", 200
    except Exception as e:
        return f"Error placing {side} order: {e}", 500

@app.route("/", methods=["GET"])
def home():
    return "NRTR Binance Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
