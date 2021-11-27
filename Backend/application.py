import configparser
import datetime
import logging
import os
from os.path import join, dirname

import boto3
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL

config = configparser.RawConfigParser()
thisfolder = os.path.dirname(os.path.abspath(__file__))
initfile = os.path.join(thisfolder, 'env.cfg')
config.read(initfile)

details_dict = dict(config.items('SECTION_NAME'))

application = Flask(__name__)

cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'

dotenv_path = join(dirname(__file__), 'env.cfg')
load_dotenv(dotenv_path)
load_dotenv(find_dotenv())
print(details_dict)
client = boto3.client("cognito-idp", region_name=details_dict['region_name'])

mysql = MySQL()
application.config['MYSQL_DATABASE_USER'] = details_dict['mysql_database_user']
application.config['MYSQL_DATABASE_PASSWORD'] = details_dict['mysql_database_password']
application.config['MYSQL_DATABASE_DB'] = details_dict['mysql_database_db']
application.config['MYSQL_DATABASE_HOST'] = details_dict['mysql_database_host']
mysql.init_app(application)
conn = mysql.connect()
cursor = conn.cursor()


@application.route('/test', methods=['POST'])
@cross_origin()
def test():
    dic = {}
    dic["ke"] = "value"
    return Response(dic, status=200, mimetype='application/json')


def subscribeToSNS(user):
    try:
        response = subscribe(details_dict['topic'], "email", user)
    except Exception as e:
        print(e)


@application.route('/stocks', methods=['POST'])
@cross_origin()
def register():
    try:

        req = request.get_json()
        print(req)
        stockNames = req['stockNames']
        stockBuyPrices = req['stockBuyPrices']
        cutOffLow = req['cutOffLow']
        cutOffHigh = req['cutOffHigh']
        username = req['username']
        cursor.execute(
            "insert into stocks (user, name, price, cutOffLow, cutOffHigh, timestamp) values (%s, %s, %s, %s, %s, %s);",
            (username, stockNames, stockBuyPrices, cutOffLow, cutOffHigh, datetime.datetime.now()))
        conn.commit()
        return Response(status=201, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(status=409, mimetype='application/json')


@application.route('/')
def nothing():
    return 'Working!'


@application.route('/', methods=['POST'])
@cross_origin()
def getUser():
    client_id = details_dict['cognito_user_client_id']
    client_secret = details_dict['client_secret']
    callback_uri = details_dict['callback_uri']
    cognito_app_url = details_dict['cognito_app_url']
    code = request.get_json()['code']
    token_url = f"{cognito_app_url}/oauth2/token"
    try:
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)

        params = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": callback_uri
        }

        response = requests.post(token_url, auth=auth, data=params)
        response = response.json()
        print(response)
        access_token = response["access_token"]
        response = client.get_user(AccessToken=access_token)
        print(response)
        username = response["Username"]
        print(username)
        subscribeToSNS(username)
        return Response(username, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(status=400, mimetype='application/json')


logger = logging.getLogger(__name__)

sns_client = boto3.client('sns', region_name='us-east-2')


def subscribe(topic, protocol, endpoint):
    """
    :param topic: The topic to subscribe to.
    :param protocol: The protocol of the endpoint, such as 'sms' or 'email'.
    :param endpoint: The endpoint that receives messages, such as a phone number
                     (in E.164 format) for SMS messages, or an email address for
                     email messages.
    :return: The newly added subscription.
    """
    try:
        subscription = sns_client.subscribe(
            TopicArn=topic, Protocol=protocol, Endpoint=endpoint, ReturnSubscriptionArn=True)
        logger.info("Subscribed %s %s to topic %s.", protocol, endpoint, topic)
    except ClientError:
        logger.exception(
            "Couldn't subscribe %s %s to topic %s.", protocol, endpoint, topic)
        raise
    else:
        return subscription


if __name__ == '__main__':
    application.run(ssl_context='adhoc', host='localhost', port=8080, debug=True)
