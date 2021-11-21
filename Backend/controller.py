import datetime
from os.path import join, dirname

import requests
from flask import Flask, request, Response, render_template
from flaskext.mysql import MySQL

# from SnsWrapper import subscribe
import os
import boto3
from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS, cross_origin
from Backend.SnsWrapper import subscribe

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

dotenv_path = join(dirname(__file__), '.env')
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


@app.route('/test', methods=['POST'])
@cross_origin()
def test():
    dic = {}
    dic["ke"] = "value"
    return Response(dic, status=200, mimetype='application/json')


def subscribeToSNS(user):
    try:
        response = subscribe(os.getenv("topic"), "email", user)
    except Exception as e:
        print(e)


@app.route('/login', methods=['POST'])
def login():
    # req = request.form
    print(request.form['username'])
    # print(req)
    username = request.form['username']
    password = request.form['password']
    try:
        response = client.initiate_auth(
            ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )

        access_token = response["AuthenticationResult"]["AccessToken"]

        response = client.get_user(AccessToken=access_token)
        return Response(status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response("Invalid Password", status=409, mimetype='application/json')


@app.route('/stocks', methods=['POST'])
def register():
    try:

        req = request.get_json()
        stockNames = req['stockNames']
        stockBuyPrices = req['stockBuyPrices']
        cutOffLow = req['cutOffLow']
        cutOffHigh = req['cutOffHigh']
        username = req['username']
        cursor.execute("insert into stocks values (%s, %s, %s, %s, %s, %s);",
                       (username, stockNames, stockBuyPrices, cutOffLow, cutOffHigh, datetime.now()))
        conn.commit()
        return Response(status=201, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(status=409, mimetype='application/json')


@app.route('/confirmCode', methods=['POST'])
def confirmCode():
    req = request.get_json()
    confirm_code = req['confirm_code']
    username = req['username']
    subscribeToSNS(username)
    try:
        response = client.confirm_sign_up(
            ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
            Username=username,
            ConfirmationCode=confirm_code,
        )
        return Response(status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(status=500, mimetype='application/json')


@app.route('/', methods=['POST'])
def getUser():
    client_id = os.getenv("COGNITO_USER_CLIENT_ID")
    client_secret = os.getenv("client_secret")
    callback_uri = os.getenv("callback_uri")
    cognito_app_url = os.getenv("cognito_app_url")
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
        access_token = response["access_token"]
        response = client.get_user(AccessToken=access_token)
        username = response["Username"]
        return Response(username, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(status=400, mimetype='application/json')


if __name__ == '__main__':
    app.run()
