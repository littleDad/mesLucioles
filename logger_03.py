# -*- coding: utf8 -*-

import logging
from logging.handlers import RotatingFileHandler
from babel.dates import format_datetime, datetime
from time import sleep

class LogFile(logging.Logger):
    '''rotatively logs erverything
    '''
    def initself(self):
        self.setLevel(logging.DEBUG)
        self.handler = RotatingFileHandler(
            'app.log',
            maxBytes=2000,  # approximatively 100 line (81)
            backupCount=1  # number of log backup files
        )
        self.addHandler(self.handler)

    def p_log(self, msg, **kwargs):
        '''level = {info, warning, debug, error}
            !!WARNINGS!! 'error' is dedicated to error formated with python
                RaiseError, and can't print anything else!
        '''
        logger = self

        if 'error' in kwargs:
            print 'error YES'
            kwargs['level'] = 'error'
        
        
        if 'level' in kwargs:
            level = kwargs['level']
        else:
            level = "info"

        if 'newline' in kwargs:
            for i in range(kwargs['newline']):
                eval("logger." + level + "(\"" + "\")")

        if 'blank' in kwargs:
            if kwargs['blank']:
                message = msg
        else:
            message = format_datetime(datetime.now(), "HH:mm:ss", locale='en')\
                + " (" + level + ") > "\
                + msg
        eval("logger." + level + "(\"" + message + "\")")
            
        # warning: error must be a python error formating!
        if level == 'error':  # or whatever you want with more details
            message = ">> " + kwargs['error'][1].message  # exc_info()[1].message
            eval("logger." + level + "(\"" + message + "\")")

if __name__ == '__main__':
    logger = LogFile('app.log')
    logger.initself()

    for i in range(10):
        sleep(.5)
        logger.p_log('coucou', level="warning")
