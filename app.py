from flask import Flask
from database import db

from api import api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(api) 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)