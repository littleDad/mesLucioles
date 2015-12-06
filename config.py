# -*- coding: utf8 -*-

from secrets import SECRET_KEY
import os

APP_NAME = "La Psycholoc"

# activates the cross-site request forgery (CSRF) prevention
WTF_CSRF_ENABLED = True 


# current dir where the Flask app is launched
basedir = os.path.abspath(os.path.dirname(__file__))


# db config
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mesLucioles.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['bat@baptabl.fr', 'al.bert95@hotmail.fr']
