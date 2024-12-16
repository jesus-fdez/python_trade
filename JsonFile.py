#!/usr/bin/env python3

import json
from datetime import datetime

class JsonFile(): 
  
    def isNewCandle(symbol, closeDate): 
        with open('data.json', 'r') as openfile:
            data = json.load(openfile)

        if data.get(symbol) is None or data.get(symbol) != closeDate:
            data[symbol] = closeDate
            with open('data.json', 'w') as f:
                json.dump(data, f)

            return True
        else:
            return False

    def getSupertrend(symbol, value):
        with open('data.json', 'r') as openfile:
            data = json.load(openfile)

        lastValue = data.get(symbol + '_supertrend')
        data[symbol + '_supertrend'] = str(value)

        with open('data.json', 'w') as f:
            json.dump(data, f)

        return lastValue

    def mustBeAlerted(symbol):
        symbol = symbol.replace("-", "")

        with open('/home/trade/' + symbol + '.txt', 'r') as f:
            value = f.readline()

        now = datetime.now().timestamp()
        diff = (now - float(value)) / 60.0

        if value == 0 or diff >= 30:
            with open('/home/trade/' + symbol + '.txt', 'w') as f:
                f.write(str(now))

            return True
        else:    
            return False
