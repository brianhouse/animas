#!/usr/bin/env python3

from housepy import config, log
import requests

try:
    r = requests.get("http://%s:%s/copper" % (config['server']['host'], config['server']['port']))
except Exception as e:
    log.error("Connection failed: %s" % e)
    exit()

with open("level.txt", 'w') as f:
    f.write(r.text)

