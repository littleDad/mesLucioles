#!env/bin/python2
# -*- coding: utf8 -*-
"""
this admin script allows you to :
  - add an user to the db : ./administration 0 email password (firstname timezone)
  - 

insert into user values (1,'bat@baptabl.fr','coucou','b@t','2015-11-24 14:58:36.667460','fr_FR');
insert into spending values (1, '2015-12-12 13:48:55.762390', 'Alimentation', 'Carottes', 20, 1);
"""

from sys import argv
from app import models
from app.models import User
from flask import Flask
from babel.dates import datetime
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

def addBill():
        bill = models.Spending()
        bill.timestamp=datetime.utcnow()
        bill.type='Alimentation'
        bill.label='Carottes2'
        bill.total=25.23
        bill.payer_id = models.User.query.filter_by(id=1).first().id
        bill_user_ids = [1, 2]
        bill.addParts(db.session, bill_user_ids)
        db.session.add(bill)
        db.session.commit()


if __name__ == '__main__':
    if argv[1] == str(0):
        email = argv[2]
        passwd = argv[3]
        try:
            firstname = argv[4]
        except:
            firstname = None
        try:
            timezone = argv[5]
        except:
            timezone = None

        addUser(email, passwd, firstname, timezone)
    if argv[1] == str(1):
        addBill()#spend=models.Spending.query.filter_by(id=1).first())
