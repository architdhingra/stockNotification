from flask import Flask, request
from flaskext.mysql import MySQL
from SnsWrapper import subscribe

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'CS218_Project'
app.config['MYSQL_DATABASE_DB'] = 'cs218projectschema'
app.config['MYSQL_DATABASE_HOST'] = 'cs218db.cmrinziqitrh.us-east-2.rds.amazonaws.com'
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
    id = req['id']
    pwd = req['password']


@app.route('/register', methods=['POST'])
def register():
    req = request.get_json()
    id = req['id']
    pwd = req['password']
    stockNames = req['stockNames']
    stockBuyPrices = req['stockBuyPrices']
    cutOffLow = req['cutOffLow']
    cutOffHigh = req['cutOffHigh']
    for i, j in enumerate(stockNames):
        print(id, stockNames[i], stockBuyPrices[i], cutOffLow[i], cutOffHigh[i])
        cursor.execute("insert into stock values (%s, %s, %s, %s, %s);", (id, stockNames[i], stockBuyPrices[i], cutOffLow[i], cutOffHigh[i]))
    conn.commit()

    return 'done'




if __name__ == '__main__':
    app.run()
