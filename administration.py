#!env/bin/python2
# -*- coding: utf8 -*-
"""
this admin script allows you to :
  - add an user to the db : ./administration email password (firstname timezone)
  - 

"""


from sys import argv
from app import models
from flask import Flask
coreApp = Flask(__name__)
coreApp.config.from_object('config')

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(coreApp)


def addUser(*args):
    """adding an user in the database: (email, passwd, firstname, timezone)"""
    #timezone = 'fr_FR'
    user = models.User(email=email, password=passwd, firstname=firstname, timezone=timezone)
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    email = argv[1]
    passwd = argv[2]
    try:
        firstname = argv[3]
    except:
        firstname = None
    try:
        timezone = argv[4]
    except:
        timezone = None

    addUser(email, passwd, firstname, timezone)