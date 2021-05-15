# -*- coding: utf8 -*-

import os

APP_NAME = "Glouthune"

from logger_04 import LogFile
LOGGER = LogFile('data/app.log')
LOGGER.initself()
LOGGER.p_log(u'démarrage de l\'appli')


# activates the cross-site request forgery (CSRF) prevention
WTF_CSRF_ENABLED = True 


# current dir where the Flask app is launched
basedir = os.path.abspath(os.path.dirname(__file__))


# db config
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mesLucioles.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['bat@baptabl.fr']


# allowing searches in spendings
WHOOSH_ENABLED = True

SECRET_KEY = os.environ['SECRET_KEY']

