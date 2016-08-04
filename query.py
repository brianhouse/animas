#!/usr/bin/env python3

import json
from housepy import config, log, util, strings
from mongo import db


results = db.entries.find()
for result in results:
    print(json.dumps(result, indent=4, default=lambda d: str(d)))