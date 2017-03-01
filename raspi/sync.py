#!/usr/bin/env python3

import requests, os, time, random, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from housepy import config, log

time.sleep(random.random() * 10.0)  # random delay to give the server some breathing room

try:
    r = requests.get("http://%s:%s/%s" % (config['server']['host'], config['server']['port'], config['metal']))
except Exception as e:
    log.error("Connection failed: %s" % e)
    exit()

with open(os.path.join(os.path.dirname(__file__), "level.txt"), 'w') as f:
    f.write(r.text)

