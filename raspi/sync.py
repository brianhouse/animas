#!/usr/bin/env python3

import requests, os
from housepy import config, log


try:
    r = requests.get("http://%s:%s/%s" % (config['server']['host'], config['server']['port'], config['metal']))
except Exception as e:
    log.error("Connection failed: %s" % e)
    exit()

with open(os.path.join(os.path.dirname(__file__), "level.txt"), 'w') as f:
    f.write(r.text)

