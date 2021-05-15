#!/usr/bin/env python
# coding: utf8

import os
from app import coreApp


http_port = os.environ.get('PORT', 7788)

coreApp.run(debug=False, port=int(http_port))

