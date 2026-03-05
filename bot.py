import os
import time
import pandas as pd
from binance.client import Client
import ta
from telegram import Bot

print("BOT STARTED")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

bot.send_message(chat_id=CHAT_ID, text="🤖 Trading Bot is online")

client = Client()

symbols = ["BTCUSDT", "ETHUSDT"]

def get_data(symbol):
    klines = client.get_klines(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_5MINUTE,
        limit=200
    )

    df = pd.DataFrame(klines, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","num_trades","taker_base_vol",
        "taker_quote_vol","ignore"
    ])

    df["close"] = df["close"].astype(float)
    return df


def check_signal(symbol):

    df = get_data(symbol)

    price = df["close"].iloc[-1]

    rsi = ta.momentum.RSIIndicator(df["close"]).rsi().iloc[-1]

    macd = ta.trend.MACD(df["close"]).macd_diff().iloc[-1]

    ema20 = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator().iloc[-1]
    ema50 = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator().iloc[-1]

    # LONG SIGNAL
    if rsi < 35 and macd > 0 and ema20 > ema50:

        tp1 = price * 1.01
        tp2 = price * 1.02
        tp3 = price * 1.04
        sl = price * 0.985

        message = f"""
🚀 LONG SIGNAL

Coin: {symbol}
Entry: {round(price,2)}

TP1: {round(tp1,2)}
TP2: {round(tp2,2)}
TP3: {round(tp3,2)}

SL: {round(sl,2)}

RSI: {round(rsi,2)}
"""

        bot.send_message(chat_id=CHAT_ID, text=message)

    # SHORT SIGNAL
    if rsi > 65 and macd < 0 and ema20 < ema50:

        tp1 = price * 0.99
        tp2 = price * 0.98
        tp3 = price * 0.96
        sl = price * 1.015

        message = f"""
🔻 SHORT SIGNAL

Coin: {symbol}
Entry: {round(price,2)}

TP1: {round(tp1,2)}
TP2: {round(tp2,2)}
TP3: {round(tp3,2)}

SL: {round(sl,2)}

RSI: {round(rsi,2)}
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
