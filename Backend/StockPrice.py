import os
import ssl

import configparser
import requests
from os.path import join, dirname
import smtplib
from flask import Flask
from flaskext.mysql import MySQL
from datetime import datetime, timedelta
import boto3

app = Flask(__name__)


config = configparser.RawConfigParser()
thisfolder = os.path.dirname(os.path.abspath(__file__))
initfile = os.path.join(thisfolder, 'env.cfg')
config.read(initfile)

details_dict = dict(config.items('SECTION_NAME'))
client = boto3.client("cognito-idp", region_name=details_dict['region_name'])

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = details_dict['mysql_database_user']
app.config['MYSQL_DATABASE_PASSWORD'] = details_dict['mysql_database_password']
app.config['MYSQL_DATABASE_DB'] = details_dict['mysql_database_db']
app.config['MYSQL_DATABASE_HOST'] = details_dict['mysql_database_host']
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
                        headers={"x-api-key": details_dict['x-api-key']})
    stocks = resp.json()["marketSummaryResponse"]["result"]
    stockDict = {}
    for stock in stocks:
        stockDict[stock["fullExchangeName"]] = stock["regularMarketPrice"]["raw"]
    print('running get all stocks')
    now = datetime.now()
    five = timedelta(minutes=5)
    cursor.execute("select * from stocks where timestamp < %s;", (now - five))
    myresult = cursor.fetchall()
    print('verifying all stocks')
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
