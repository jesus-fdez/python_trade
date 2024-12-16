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
_range = '260m' # Min 20 periods

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
    candles = wma(candles)
    
    return candles

def wma(candles):
    candles.insert(loc=5, column='wma', value=float("nan"))
    wmaAvg = 0

    for i in range(1, period + 1):
        wmaAvg = wmaAvg + i

    for pos in reversed(range(len(candles.RSI_14))):
        nextpos = 0
        avg = 0

        if pos < period:
            return candles

        for i in reversed(range(1, period + 1)):
            avg = avg + (candles.RSI_14[pos - nextpos] * i)
            nextpos = nextpos + 1

        candles['wma'][pos] = avg/wmaAvg
    
    return candles


def initLog():
    print(str(datetime.datetime.now()) + ' RSI ' + symbol)


# ==================================== script


# -4 -3 -2 -1
#  |  |  |  .

time.sleep(3)

initLog()

maxClose = 0.0
maxIndex = 0
alertMsg = ""
sendAlert = False 

rsiDown = 35
rsiUp = 65

symbol = symbol.replace("=X", "")
candles, date = getData()
candles = getIndicators(candles)

low = candles.low
high = candles.high
close = candles.close
open = candles.open
rsi = candles.RSI_14
rsiWma = candles.wma

if rsi.iloc[-1] <= rsiDown:
    for index in range(-4, -27):
        if (close.iloc[-3] <= close.iloc[-2] # Cierre de la vela que se evalúa es <= a la actual
         and low.iloc[-3] < low.iloc[-4] # El high de la que se evalúa es > a su anterior (forma pico)
         and low.iloc[index] <= low[index + 1] # La vela destino forma pico
         and low.iloc[index] < low[index - 1] # La vela destino forma pico
         and low.iloc[index] > low.iloc[-3] # El high de la vela target es menor que la que se evalúa
         and rsi.iloc[index] <= rsi.iloc[-3] # Para la divergencia, el rsi del target debe ser >= a la que se evalúa
         and (maxClose == 0 or low.iloc[index] < maxClose)
         and rsiWma.iloc[-3] > rsi.iloc[-3]):
            maxClose = low.iloc[index]
            maxIndex = index

    if maxIndex > 0:
        sendAlert = True
        alertMsg = "Long moment divergence 1"
        telegram(symbol + ': RSI ' + alertMsg + ' 🟢')

maxClose = 0
maxIndex = 0

if rsi.iloc[-1] >= rsiUp:
    for index in range(-4, -27):
        if (close.iloc[-3] >= close.iloc[-2] # Cierre de la vela que se evalúa es <= a la actual
         and low.iloc[-3] > low.iloc[-4] # El high de la que se evalúa es > a su anterior (forma pico)
         and low.iloc[index] >= low[index + 1] # La vela destino forma pico
         and low.iloc[index] > low[index - 1] # La vela destino forma pico
         and low.iloc[index] < low.iloc[-3] # El high de la vela target es menor que la que se evalúa
         and rsi.iloc[index] >= rsi.iloc[-3] # Para la divergencia, el rsi del target debe ser >= a la que se evalúa
         and (maxClose == 0 or low.iloc[index] > maxClose)
         and rsiWma.iloc[-3] < rsi.iloc[-3]):
            maxClose = high.iloc[index]
            maxIndex = index

    if maxIndex > 0:
        sendAlert = True
        alertMsg = "Short moment divergence 1"
        telegram(symbol + ': RSI ' + alertMsg + ' 🔴')

maxClose = 0
maxIndex = 0

if rsi.iloc[-2] <= rsiDown:
    for index in range(-3, -6):
        if (rsi.iloc[index] < rsi.iloc[-2]
         and close.iloc[index] > close.iloc[-2]
         and low.iloc[-2] <= low.iloc[-3]
         and high.iloc[-2] >= high.iloc[-3]
         and rsiWma.iloc[-2] > rsi.iloc[-2]
         and (maxClose == 0 or close.iloc[index] < maxClose)):
            maxClose = close.iloc[index]
            maxIndex = index
    
    if maxIndex > 0:
        sendAlert = True
        alertMsg = "Long moment divergence 2"
        telegram(symbol + ': RSI ' + alertMsg + ' 🟢')

maxClose = 0
maxIndex = 0

if rsi.iloc[-2] >= rsiUp:
    for index in range(-3, -6):
        if (rsi.iloc[index] > rsi.iloc[-2]
         and close.iloc[index] < close.iloc[-2]
         and low.iloc[-2] >= low.iloc[-3]
         and high.iloc[-2] <= high.iloc[-3]
         and rsiWma.iloc[-2] < rsi.iloc[-2]
         and (maxClose == 0 or close.iloc[index] > maxClose)):
            maxClose = close.iloc[index]
            maxIndex = index
        
    if maxIndex > 0:
        sendAlert = True
        alertMsg = "Short moment divergence 2"
        telegram(symbol + ': RSI ' + alertMsg + ' 🔴')


# ---------------------------- #

if (close.iloc[-3] > open.iloc[-3]
 and close.iloc[-2] < open.iloc[-2]
 and open.iloc[-2] >= close.iloc[-3]
 and close.iloc[-2] <= open.iloc[-3]
 and rsi.iloc[-3] >= rsiUp
 and rsi.iloc[-3] > rsiWma.iloc[-3]):
    sendAlert = True
    alertMsg = "Short involute"
    telegram(symbol + ': RSI ' + alertMsg + ' 🔴')

if (close.iloc[-3] < open.iloc[-3]
 and close.iloc[-2] > open.iloc[-2]
 and open.iloc[-2] <= close.iloc[-3]
 and close.iloc[-2] >= open.iloc[-3]
 and rsi.iloc[-3] <= rsiDown
 and rsi.iloc[-3] < rsiWma.iloc[-3]):
    sendAlert = True
    alertMsg = "Long involute"
    telegram(symbol + ': RSI ' + alertMsg + ' 🟢')
