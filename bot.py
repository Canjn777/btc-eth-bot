import os
import time
import pandas as pd
from binance.client import Client
import ta
from telegram import Bot
import asyncio

print("BOT STARTED")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

async def send_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

# 启动提醒
asyncio.run(send_message("🤖 交易机器人已启动，正在监控 BTC 和 ETH"))

client = Client()

symbols = ["BTCUSDT", "ETHUSDT"]

last_signal = {}


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
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    return df


def check_signal(symbol):

    df = get_data(symbol)

    price = df["close"].iloc[-1]

    rsi = ta.momentum.RSIIndicator(df["close"]).rsi().iloc[-1]

    macd = ta.trend.MACD(df["close"]).macd_diff().iloc[-1]

    ema20 = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator().iloc[-1]
    ema50 = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator().iloc[-1]

    atr = ta.volatility.AverageTrueRange(
        df["high"],
        df["low"],
        df["close"]
    ).average_true_range().iloc[-1]

    signal = None

    if rsi < 40 and macd > 0 and ema20 > ema50:
        signal = "LONG"

    if rsi > 60 and macd < 0 and ema20 < ema50:
        signal = "SHORT"

    if signal:

        if last_signal.get(symbol) == signal:
            return

        last_signal[symbol] = signal

        if signal == "LONG":

            tp1 = price + atr
            tp2 = price + atr * 2
            tp3 = price + atr * 3
            sl = price - atr

        else:

            tp1 = price - atr
            tp2 = price - atr * 2
            tp3 = price - atr * 3
            sl = price + atr

        message = f"""
🔥 {signal} SIGNAL

Coin: {symbol}

Entry: {round(price,2)}

TP1: {round(tp1,2)}
TP2: {round(tp2,2)}
TP3: {round(tp3,2)}

SL: {round(sl,2)}

RSI: {round(rsi,2)}
"""

        asyncio.run(send_message(message))


while True:

    try:

        for symbol in symbols:

            check_signal(symbol)

        time.sleep(300)

    except Exception as e:

        print("Error:", e)

        time.sleep(60)
