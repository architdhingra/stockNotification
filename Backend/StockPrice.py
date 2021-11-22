import ssl

import requests
from os.path import join, dirname
import smtplib
from flask import Flask
from flaskext.mysql import MySQL
from datetime import datetime, timedelta
import os
import boto3
from dotenv import load_dotenv, find_dotenv

app = Flask(__name__)

dotenv_path = join(dirname(__file__), 'env.cfg')
frontend_path = join(dirname(__file__), 'Frontend', 'postlogin.html')
load_dotenv(dotenv_path)
load_dotenv(find_dotenv())
client = boto3.client("cognito-idp", region_name=os.getenv("region_name"))

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = os.getenv("MYSQL_DATABASE_USER")
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv("MYSQL_DATABASE_PASSWORD")
app.config['MYSQL_DATABASE_DB'] = os.getenv("MYSQL_DATABASE_DB")
app.config['MYSQL_DATABASE_HOST'] = os.getenv("MYSQL_DATABASE_HOST")
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()


def sendEmail(cutOffLow, cutOffHigh, stockName, stockPrice, user):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "team9cmpe275@gmail.com"
    receiver_email = user
    password = "cmpe275project"
    message = """Subject: Stock Notification

    Hi, your stock {stockName} has crossed the range {stockPrice} - {cutOffHigh} at current price 
    {stockPrice}. Please consider selling your stock. """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.format(stockName=stockName, stockPrice=stockPrice,
                                                                     cutOffLow=cutOffLow, cutOffHigh=cutOffHigh))


def getAllStocks():
    resp = requests.get("https://yfapi.net/v6/finance/quote/marketSummary",
                        headers={"x-api-key": os.getenv("x-api-key")})
    stocks = resp.json()["marketSummaryResponse"]["result"]
    stockDict = {}
    for stock in stocks:
        stockDict[stock["fullExchangeName"]] = stock["regularMarketPrice"]["raw"]

    now = datetime.now()
    five = timedelta(minutes=5)
    cursor.execute("select * from stocks where timestamp < %s;", (now - five))
    myresult = cursor.fetchall()
    for result in myresult:
        userStockName = result[1]
        cutOffLow = float(result[3])
        cutOffHigh = float(result[4])
        id = int(result[6])
        if userStockName in stockDict:
            cursor.execute("update stocks set timestamp = %s where id = %s", (now, id))
            if cutOffLow <= stockDict[userStockName] or cutOffHigh >= stockDict[userStockName]:
                sendEmail(cutOffLow, cutOffHigh, userStockName, stockDict[userStockName], result[0])
            conn.commit()


getAllStocks()
