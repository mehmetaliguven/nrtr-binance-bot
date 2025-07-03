from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET')
client = Client(api_key, api_secret)

SYMBOL = "AVAXUSDT"
QUANTITY = 5  # Her işlemde sabit 5 AVAX

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data["side"] == "buy":
        try:
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=QUANTITY
            )
            return "Buy Order Executed", 200
        except Exception as e:
            return f"Buy Error: {e}", 500

    elif data["side"] == "sell":
        try:
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=QUANTITY
            )
            return "Sell Order Executed", 200
        except Exception as e:
            return f"Sell Error: {e}", 500

    return "Invalid Payload", 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
