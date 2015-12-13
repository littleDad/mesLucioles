#!env/bin/python2
# -*- coding: utf8 -*-
"""
this admin script allows you to :
  - la base minimale du programme : ./administration 1
  - base de test : ./administration 2
  - add an user to the db : ./administration 0 email password (firstname timezone)

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
        bill.payer_id = 1#models.User.query.filter_by(id=1).first().id
        bill_user_ids = [1]
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
        t1 = models.Spending.Type(name=u"Alimentation")
        db.session.add(t1)
        t2 = models.Spending.Type(name=u"Alcool")
        db.session.add(t2)
        t3 = models.Spending.Type(name=u"Divers")
        db.session.add(t3)
        t4 = models.Spending.Type(name=u"Charges")
        db.session.add(t4)
        t5 = models.Spending.Type(name=u"Bien-être")
        db.session.add(t5)
        db.session.commit()

    if argv[1] == str(2):
        db.session.add(models.User(email='b@t', password='coucou', firstname='Batoo'))
        db.session.add(models.User(email='b@2t', password='coucou'))
        addBill()#spend=models.Spending.query.filter_by(id=1).first())
        
        db.session.commit()
