import os
import time
from flask import Flask, request
from binance.client import Client
from binance.enums import *

app = Flask(__name__)

# Binance API anahtarları
API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')

client = Client(API_KEY, API_SECRET)

SYMBOL = "AVAXUSDT"
QTY = 5  # Her işlemde 5 adet AVAX

@app.route('/')
def home():
    return "NRTR Binance Bot is running."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data or 'side' not in data:
        return "Invalid payload", 400

    side = data['side']

    try:
        if side == 'buy':
            order = client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=QTY
            )
            return "Buy Order Executed", 200

        elif side == 'sell':
            order = client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=QTY
            )
            return "Sell Order Executed", 200

        else:
            return "Invalid side", 400

    except Exception as e:
        return f"Error: {str(e)}", 500

# Render için port ayarı
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
