#!/usr/bin/env python3

import json
import numpy as np
import signal_processing as sp
from housepy import config, log, util, drawing
from mongo import db
from colors import colors


site = '09358550'
print(config['sites'][site])
query = {'site': site, 't_utc': {'$gt': util.timestamp(util.parse_date("2016-07-28", tz=config['tz']))}}
log.info(query)
results = db.entries.find(query)
results = list(results)
print(json.dumps(results[0], indent=4, default=lambda d: str(d)))

ts = [d['t_utc'] for d in results]
signals = []
labels = list(config['labels'].values())
labels.sort()
for i, label in enumerate(labels):
    log.info(label)
    values = [d[label] if label in d else None for d in results]
    values = sp.remove_shots(values, nones=True)  # repair missing values    
    signal = sp.resample(ts, values)
    signal = sp.normalize(signal)
    signals.append(signal)

points = []
for i in range(len(signals[0])):
    point = [signal[i] for signal in signals]
    points.append(point)

points = np.array(points)

for point in points:
    print(point)