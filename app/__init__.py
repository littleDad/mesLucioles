# -*- coding: utf8 -*-

# main
from flask import Flask
coreApp = Flask(__name__)
coreApp.config.from_object('config')


# db
#from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(coreApp) ### à terme, cccDb ?


# sessions, users and logins
import os
from flask.ext.login import LoginManager # handle our users logged in state
from config import basedir
lm = LoginManager() ### à terme, cccLm ?
lm.init_app(coreApp)
lm.login_view = 'login' # specifies the view which logs users in (for @login_required decorator)


from app import views, models


# bug mail report on production
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
if not coreApp.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'coreApp failure on baptabl production server', credentials)
    mail_handler.setLevel(logging.ERROR)
    coreApp.logger.addHandler(mail_handler)



# log into file
if not coreApp.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('data/coreApp.log', 'a', 1 * 1024 * 1024, 10) # log file size limited to 1Mb ; keep last 10 log files as backup
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    coreApp.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    coreApp.logger.addHandler(file_handler)
    coreApp.logger.info('coreApp startup')
