from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book

# Create a Flask app instance
app = Flask(__name__)

# Configure SQLite database using absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

# Initialize Flask app for SQLAlchemy
db.init_app(app)