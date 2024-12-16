#!/usr/bin/env python3

import requests
import datetime
import pandas_ta as ta
import json
import warnings
import hmac
import hashlib
import base64
import time
import sys
from JsonFile import JsonFile


# ==================================== params

symbol = sys.argv[1] #'ETH-USD'
period = 14
interval = '5m'
_range = '150m' # Min 20 periods

warnings.simplefilter(action='ignore', category=FutureWarning)

# ==================================== defs


def telegram(message):
    token = "== TELEGRAM TOKEN =="
    chat_id = "== TELEGRAM CHAT ID =="
    url = "https://api.telegram.org/bot" + token + "/sendMessage?chat_id="+ chat_id +"&text=" + message
    requests.get(url)


def getData():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/"+ symbol +"?region=US&lang=en-US&includePrePost=false&interval=" + interval + "&useYfid=true&range=" + _range
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=headers)

    candles = ta.DataFrame(response.json()['chart']['result'][0]['indicators']['quote'][0], columns=['close', 'open', 'high', 'low'])
    date = datetime.datetime.fromtimestamp(response.json()['chart']['result'][0]['timestamp'][-1])
    return candles, date

def wma(candles):
    candles.insert(loc=5, column='wma', value=float("nan"))
    wmaAvg = 0

    for i in range(1, period + 1):
        wmaAvg = wmaAvg + i


    for pos in reversed(range(len(candles.close))):
        nextpos = 0
        avg = 0

        if pos < period:
            return candles

        for i in reversed(range(1, period + 1)):
            avg = avg + (candles.close[pos - nextpos] * i)
            nextpos = nextpos + 1

        candles['wma'][pos] = avg/wmaAvg
    
    return candles


def getIndicators(candles):
    candles.ta.rsi(length=period, append=True)
    canldes = wma(candles)

    return candles


def initLog():
    print(str(datetime.datetime.now()) + ' RSI-WMA ' + symbol)


# ==================================== script


time.sleep(30)
candles, date = getData()

if not JsonFile.isNewCandle(symbol, str(date)):
    exit(1)

initLog()
candles = getIndicators(candles)

rsi40Found = False
rsi60Found = False

for i in range(1, period + 1):
    if candles.RSI_14[i] <= 40:
        rsi40Found = True
    if candles.RSI_14[i] >= 60:
        rsi60Found = True

if candles.low.iloc[-2] < candles.wma.iloc[-2] and candles.high.iloc[-2] > candles.wma.iloc[-2] and rsi40Found:
    telegram(symbol + ': RSI-WMA buy signal')

if candles.high.iloc[-2] > candles.wma.iloc[-2] and candles.low.iloc[-2] < candles.wma.iloc[-2] and rsi60Found:
    telegram(symbol + ': RSI-WMA sell signal')
