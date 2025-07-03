from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

# Binance API Anahtarları
API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')
client = Client(API_KEY, API_SECRET)

# İşlem yapılacak sembol ve kaldıraç
SYMBOL = "AVAXUSDT"
LEVERAGE = 5
ORDER_QUANTITY = 5  # Sabit 5 adet işlem

# Kaldıraç ayarı (ilk çalışmada bir kere yapılır)
try:
    client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)
except Exception as e:
    print(f"Kaldıraç ayarlanamadı: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'side' not in data:
        return "Geçersiz veri", 400

    side = data['side'].lower()

    try:
        if side == 'buy':
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=ORDER_QUANTITY
            )
            print("✅ ALIM emri gönderildi.")
            return "Buy order executed", 200

        elif side == 'sell':
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=ORDER_QUANTITY
            )
            print("✅ SATIM emri gönderildi.")
            return "Sell order executed", 200

        else:
            return "Bilinmeyen işlem türü", 400

    except Exception as e:
        print(f"HATA: {e}")
        return "İşlem gerçekleştirilemedi", 500

@app.route('/')
def home():
    return "NRTR Binance Bot Aktif", 200
