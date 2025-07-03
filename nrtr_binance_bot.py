
from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

SYMBOL = "AVAXUSDT"
QUANTITY = 10
TRAILING_PERCENT = 2.0  # %2 geri çekilme toleransı

current_position = None  # "long", "short", or None

@app.route("/webhook", methods=["POST"])
def webhook():
    global current_position

    data = request.get_json()
    if not data or "side" not in data:
        return jsonify({"error": "Invalid request"}), 400

    side = data["side"]
    mark_price = float(client.futures_mark_price(symbol=SYMBOL)["markPrice"])

    if side == "buy":
        if current_position == "long":
            return jsonify({"message": "Already in long position"}), 200
        elif current_position == "short":
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=QUANTITY
            )
            current_position = None

        client.futures_create_order(
            symbol=SYMBOL,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=QUANTITY
        )

        client.futures_create_order(
            symbol=SYMBOL,
            side=SIDE_SELL,
            type=ORDER_TYPE_TRAILING_STOP_MARKET,
            quantity=QUANTITY,
            callbackRate=TRAILING_PERCENT,
            activationPrice=str(round(mark_price * 1.01, 2)),
            reduceOnly=True
        )

        current_position = "long"
        return jsonify({"message": "Long with trailing stop placed"}), 200

    elif side == "sell":
        if current_position == "short":
            return jsonify({"message": "Already in short position"}), 200
        elif current_position == "long":
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=QUANTITY
            )
            current_position = None

        client.futures_create_order(
            symbol=SYMBOL,
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=QUANTITY
        )

        client.futures_create_order(
            symbol=SYMBOL,
            side=SIDE_BUY,
            type=ORDER_TYPE_TRAILING_STOP_MARKET,
            quantity=QUANTITY,
            callbackRate=TRAILING_PERCENT,
            activationPrice=str(round(mark_price * 0.99, 2)),
            reduceOnly=True
        )

        current_position = "short"
        return jsonify({"message": "Short with trailing stop placed"}), 200

    return jsonify({"error": "Invalid side"}), 400

@app.route("/")
def home():
    return "Trailing Stop Bot Aktif", 200
