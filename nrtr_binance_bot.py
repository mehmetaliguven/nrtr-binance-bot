
from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

SYMBOL = "AVAXUSDT"
TRAILING_PERCENT = 2.0  # %2 trailing stop

def calculate_quantity():
    balance = float(client.futures_account_balance()[0]['balance'])
    usdt_amount = balance * 0.25  # %25 risk
    mark_price = float(client.futures_mark_price(symbol=SYMBOL)['markPrice'])
    qty = (usdt_amount * 5) / mark_price  # 5x kaldıraç
    return round(qty, 1)  # AVAX için 1 ondalık basamak

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    side = data.get("side", "").lower()

    if side not in ["buy", "sell"]:
        return "Invalid side", 400

    try:
        # Mevcut pozisyonu kontrol et ve kapat
        positions = client.futures_position_information(symbol=SYMBOL)
        position_amt = float(positions[0]["positionAmt"])

        if position_amt != 0:
            if position_amt > 0 and side == "sell":
                client.futures_create_order(
                    symbol=SYMBOL,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=round(abs(position_amt), 1)
                )
            elif position_amt < 0 and side == "buy":
                client.futures_create_order(
                    symbol=SYMBOL,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity=round(abs(position_amt), 1)
                )

        qty = calculate_quantity()
        mark_price = float(client.futures_mark_price(symbol=SYMBOL)['markPrice'])

        if qty <= 0 or mark_price <= 0:
            return "Quantity or price invalid", 400

        if side == "buy":
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
            try:
                client.futures_create_order(
                    symbol=SYMBOL,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_TRAILING_STOP_MARKET,
                    quantity=qty,
                    callbackRate=TRAILING_PERCENT,
                    activationPrice=str(round(mark_price * 1.01, 2)),
                    reduceOnly=True
                )
            except Exception as e:
                print(f"Trailing stop error (buy): {e}")

        elif side == "sell":
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
            try:
                client.futures_create_order(
                    symbol=SYMBOL,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_TRAILING_STOP_MARKET,
                    quantity=qty,
                    callbackRate=TRAILING_PERCENT,
                    activationPrice=str(round(mark_price * 0.99, 2)),
                    reduceOnly=True
                )
            except Exception as e:
                print(f"Trailing stop error (sell): {e}")

        return f"{side.capitalize()} order executed with trailing stop", 200

    except Exception as e:
        return f"General Error: {str(e)}", 500

@app.route("/")
def home():
    return "NRTR Güvenli Trailing Stop Bot Aktif!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
