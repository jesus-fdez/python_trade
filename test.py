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


def getIndicators(candles):
    candles.ta.rsi(length=period, append=True)
    
    return candles


def initLog():
    print(str(datetime.datetime.now()) + ' RSI ' + symbol)


# ==================================== script


if JsonFile.mustBeAlerted(symbol):
    telegram(symbol + ' test')