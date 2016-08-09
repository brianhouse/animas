#!/usr/bin/env python3

import json
import numpy as np
import signal_processing as sp
from housepy import config, log, util, drawing, strings
from mongo import db
from colors import colors

ctx = drawing.Context(1200, 500, margin=20, hsv=True)

site = "09358550"
# start = "2016-04-07"
# start = "2016-04-15"

# stop = "2016-04-16"
# start = "2016-05-01"

start = "2016-04-06"
# start = "2016-04-15"
# stop = "2016-05-30"

start = "2016-07-07"
# start = "2016-08-01"
stop = "2016-08-07"

print(config['sites'][site])
query = {'site': site, 't_utc': {'$gt': util.timestamp(util.parse_date(start, tz=config['tz'])), '$lt': util.timestamp(util.parse_date(stop, tz=config['tz']))}}
log.info(query)
results = db.entries.find(query)
results = list(results)
print(json.dumps(results[0], indent=4, default=lambda d: str(d)))

ts = [d['t_utc'] for d in results]
duration = ts[-1] - ts[0]
print("DURATION %s %s" % (duration, strings.format_time(duration)))
signals = []
rates = []
labels = list(config['labels'].values())
labels.sort()
for i, label in enumerate(labels):
    log.info(label)
    try:
        values = [d[label] if label in d else None for d in results]
        values = sp.remove_shots(values, nones=True)  # repair missing values
        signal = sp.resample(ts, values)
        num_samples = len(signal)
        sample_rate = num_samples / duration
        rates.append(sample_rate)
        signal = sp.normalize(signal)
        signal = sp.smooth(signal, 15)
        signals.append(signal)        
        # color = colors[i]
        color = i / len(labels), .8, .8, 1.
        ctx.plot(signal, stroke=color, thickness=2)
        ctx.line(10 / ctx.width, 1 - ((10 + (i * 10)) / ctx.height), 30 / ctx.width, 1 - ((10 + (i * 10)) / ctx.height), stroke=color, thickness=2)
        ctx.label(35 / ctx.width, 1 - ((13 + (i * 10)) / ctx.height), label.upper(), size=8)            
    except KeyError as e:
        log.error(log.exc(e))
        log.error(values)

ctx.output("charts/")

points = []
for i in range(len(signals[0])):
    point = [signal[i] for signal in signals]
    points.append(point)

points = np.array(points)
util.save("data/%s.pkl" % util.timestamp(), (points, rates))
util.save("data/last.pkl", (points, rates))
