#!/usr/bin/env python3

import json
import signal_processing as sp
from housepy import config, log, util, drawing
from mongo import db
from colors import colors

ctx = drawing.Context(1200, 500, margin=20)

site = '09358550'
print(config['sites'][site])
query = {'site': site, 't_utc': {'$gt': util.timestamp(util.parse_date("2016-07-28", tz=config['tz']))}}
log.info(query)
results = db.entries.find(query)
results = list(results)
print(json.dumps(results[0], indent=4, default=lambda d: str(d)))

ts = [d['t_utc'] for d in results]

for i, label in enumerate(config['labels'].values()):
    log.info(label)
    try:
        values = [d[label] if label in d else 0 for d in results]
        signal = sp.resample(ts, values)
        signal = sp.normalize(signal)
        color = colors[i]
        ctx.plot(signal, stroke=color, thickness=2)
        ctx.line(10 / ctx.width, 1 - ((10 + (i * 10)) / ctx.height), 30 / ctx.width, 1 - ((10 + (i * 10)) / ctx.height), stroke=color, thickness=2)
        ctx.label(35 / ctx.width, 1 - ((13 + (i * 10)) / ctx.height), label.upper(), size=8)            
    except Exception as e:
        log.error(log.exc(e))
        log.error(values)

ctx.output("charts/")
