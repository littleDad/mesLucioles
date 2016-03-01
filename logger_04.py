# -*- coding: utf8 -*-

import logging
from logging.handlers import RotatingFileHandler
from babel.dates import format_datetime, datetime
from time import sleep

from traceback import print_exception, format_exception

class LogFile(logging.Logger):
    '''rotatively logs erverything
    '''
    def initself(self):
        self.setLevel(logging.DEBUG)
        self.handler = RotatingFileHandler(
            'app.log',
            # maxBytes=2000,  # approximatively 100 line (81)
            maxBytes=6000,
            backupCount=3  # number of log backup files
        )
        self.addHandler(self.handler)

    def p_log(self, msg, **kwargs):
        '''level = {info, warning, debug, error}
        you can also use an exception=exc_info() argument to uprising exceptions!
        '''
        logger = self

        if 'error' in kwargs:
            print 'error YES'
            kwargs['level'] = 'error'
        
        if 'exception' in kwargs:
            print 'exception YES'
            kwargs['level'] = 'exception'

        if 'level' in kwargs:
            level = kwargs['level']
        else:
            level = "info"

        # warning: error must be a python error formating!
        if level == 'error':  # or whatever you want with more details
            message = ">> " + kwargs['error'][1].message  # exc_info()[1].message
            eval("logger." + level + "(\"" + message + "\")")
        
        elif level == 'exception':
            message = ">> UPRISING OF AN EXCEPTION!"
            eval("logger." + level + "(\"" + message + "\")")
            for line in format_exception(kwargs['exception'][0], kwargs['exception'][1], kwargs['exception'][2]):
                logger.error(line)

        else:
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
            

if __name__ == '__main__':
    logger = LogFile('app.log')
    logger.initself()

    for i in range(10):
        sleep(.5)
        logger.p_log('coucou', level="warning")
