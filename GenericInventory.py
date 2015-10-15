from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os.path, json


basepath = os.path.dirname(__file__)
# json file is in the directory above
# db_path = os.path.abspath(os.path.join(basepath, "..", "dbconfig.json"))
# db_config = open(db_path, 'r')
# db_info = json.loads(db_config.readline())

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://localhost:3306/test'
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://{user}:{passwd}@{host}/{db}".\
#                                         format(user=db_info['user'],
#                                                passwd=db_info['passwd'],
#                                                host=db_info['host'],
#                                                db=db_info['db'])
app.secret_key = "secret"
db = SQLAlchemy(app)
import views, database
