import requests
from flask import request


def getCurrentPrice(stock="AAPL"):
    resp = requests.get("https://yfapi.net/v6/finance/quote?region=US&lang=en&symbols=" + stock,
                       headers={"x-api-key": "Ol3iLb65Ld7N5nAEyq6CW9DBGsOjL2dt4WuLm1sl"})
    stockPrice = resp.json()["quoteResponse"]["result"][0]["regularMarketPrice"]
    print(stockPrice)


if __name__ == '__main__':
    getCurrentPrice()
