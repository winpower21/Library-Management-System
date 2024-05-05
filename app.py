from flask import Flask
from application.database import *
from application.functions import create_folder
import os


app = None
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT,'static','files')

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///librarydata.sqlite3'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = "absolutelysecretkey"
    db.init_app(app)
    whooshee.init_app(app)
    app.app_context().push()
    return app, db

app, db = create_app()

from application.controllers import *

with app.app_context():
    whooshee.reindex()


if __name__ == '__main__':
    create_folder(UPLOAD_FOLDER)
    app.run(debug=True)