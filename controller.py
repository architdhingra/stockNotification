from os.path import join, dirname

from flask import Flask, request, Response
from flaskext.mysql import MySQL

from SnsWrapper import subscribe
import os
import boto3
from dotenv import load_dotenv, find_dotenv

app = Flask(__name__)

dotenv_path = join(dirname(__file__), '.env')
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


@app.route('/')
def hello_world():
    response = subscribe("arn:aws:sns:us-east-2:229956378987:cs218projectnotification", "email", "myemail@host")
    return 'Hello World!'


@app.route('/login')
def login():
    req = request.get_json()
    username = req['username']
    password = req['password']
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


@app.route('/register', methods=['POST'])
def register():
    req = request.get_json()
    stockNames = req['stockNames']
    stockBuyPrices = req['stockBuyPrices']
    cutOffLow = req['cutOffLow']
    cutOffHigh = req['cutOffHigh']
    username = req['username']
    password = req['password']

    try:
        response = client.sign_up(
            ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
            Username=username,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": username}],
        )
        for i, j in enumerate(stockNames):
            print(id, stockNames[i], stockBuyPrices[i], cutOffLow[i], cutOffHigh[i])
            cursor.execute("insert into stock values (%s, %s, %s, %s, %s);",
                           (id, stockNames[i], stockBuyPrices[i], cutOffLow[i], cutOffHigh[i]))
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


if __name__ == '__main__':
    app.run()
