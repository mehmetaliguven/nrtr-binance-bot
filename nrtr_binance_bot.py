from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

SYMBOL = "AVAXUSDT"

def calculate_quantity():
    balance = float(client.futures_account_balance()[0]['balance'])
    usdt_amount = balance * 0.25  # %25 risk
    mark_price = float(client.futures_mark_price(symbol=SYMBOL)['markPrice'])
    qty = (usdt_amount * 5) / mark_price  # 5x kaldıraç
    return round(qty, 1)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    side = data.get("side", "").lower()

    if side not in ["buy", "sell"]:
        return "Invalid side", 400

    try:
        positions = client.futures_position_information(symbol=SYMBOL)
        if positions:
            position_amt = float(positions[0]["positionAmt"])
        else:
            position_amt = 0

        if position_amt != 0:
            logging.info(f"Closing existing position: {position_amt}")
            close_side = SIDE_SELL if position_amt > 0 else SIDE_BUY
            client.futures_create_order(
                symbol=SYMBOL,
                side=close_side,
                type=ORDER_TYPE_MARKET,
                quantity=round(abs(position_amt), 1)
            )

        qty = calculate_quantity()
        if qty <= 0:
            return "Quantity calculation error", 400

        order_side = SIDE_BUY if side == "buy" else SIDE_SELL
        client.futures_create_order(
            symbol=SYMBOL,
            side=order_side,
            type=ORDER_TYPE_MARKET,
            quantity=qty
        )

        logging.info(f"{side.upper()} order executed with qty: {qty}")
        return f"{side.upper()} order executed", 200

    except Exception as e:
        logging.error(f"Execution Error: {e}")
        return f"Execution Error: {str(e)}", 500

@app.route("/")
def home():
    return "NRTR BOT STABİL SÜRÜM AKTİF ✅", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
