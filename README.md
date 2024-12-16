# PYTHON TRADE

## Primer proyecto para aprendizaje de Python.

Usando el API __YAHOO Finance__, envía alertas de indicadores a __Telegram__

Consta de dos scripts:
- wma_rsi.py: Envía alerta cuando el indicador WMA-RSI arroja un valor interesante, configurado como constante.
- rsi.py: Envía alerta cuando el indicador RSI arroja un valor interesante, configurado como constante.

## Archivos auxiliares

Cada símbolo que queremos vigilar, recibido como parámetro (ejemplo: ETH-USD), tiene una entrada en `data.json` para controlar que no se envía más de una alerta para el mismo candle. Además contiene `test.py` para testear el envío de una alerta a Telegram en un momento puntual.

## Necesario para lanzar el proyecto

```
install python
python3 -m ensurepip
pip3 install requests
pip3 install pandas_ta
pip3 install pkg_resources
pip3 install setuptools
pip3 install backtesting
```

## Ejecución con Python 3:

```
python3 rsi.py ETH-USD
```

## Configuración

1. JsonFile.py: Ruta absoluta del fichero `data.json`
2. Scripts `rsi.py` y `wma_rsi.py`:
   - Constantes declaradas al inicio del script
   - Token y chat ID de telegram
