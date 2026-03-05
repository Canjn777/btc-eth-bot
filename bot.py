import os
import time
import requests
import pandas as pd
from binance.client import Client
import ta
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

client = Client()

symbols = ["BTCUSDT", "ETHUSDT"]

def get_data(symbol):
    klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=100)
    df = pd.DataFrame(klines, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","num_trades","taker_base_vol",
        "taker_quote_vol","ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df

def check_signal(symbol):

    df = get_data(symbol)

    rsi = ta.momentum.RSIIndicator(df["close"]).rsi().iloc[-1]
    price = df["close"].iloc[-1]

    if rsi < 30:
        message = f"""
🚨 BUY SIGNAL

Coin: {symbol}
Price: {price}
RSI: {round(rsi,2)}

Oversold market
Possible bounce
"""
        bot.send_message(chat_id=CHAT_ID, text=message)

    if rsi > 70:
        message = f"""
⚠️ SELL SIGNAL

Coin: {symbol}
Price: {price}
RSI: {round(rsi,2)}

Overbought market
Possible pullback
"""
        bot.send_message(chat_id=CHAT_ID, text=message)

while True:

    try:

        for symbol in symbols:
            check_signal(symbol)

        time.sleep(300)

    except Exception as e:
        print(e)
        time.sleep(60)
