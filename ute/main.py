#!/usr/bin/env python3

import csv, sys, json
import numpy as np
import signal_processing as sp
from housepy import strings, timeutil, log, drawing, util

discharge_cfs = util.load("ute_2015_discharge_cfs.pkl")
discharge_cfs_2 = util.load("ute_2015_discharge_cfs_2.pkl")
ph = util.load("ute_2015_ph.pkl")
oxygen = util.load("ute_2015_oxygen_mgl.pkl")

discharge_cfs += discharge_cfs_2
discharge_cfs.sort(key=lambda d: d['t_utc'])

streams = { 'discharge_cfs': discharge_cfs,
            'ph': ph,
            'oxygen_mgl': oxygen,
            }

log.info("Processing...")

tses = {}
for label, results in streams.items():
    ts = [v['t_utc'] for v in results]
    duration = ts[-1] - ts[0]
    log.info("--> duration (%s)\t%s %s %s" % (label, timeutil.seconds_to_string(duration), timeutil.t_to_string(ts[0]), timeutil.t_to_string(ts[-1])))
    tses[label] = ts

t_min = min([ts[0] for ts in tses.values()])
t_max = max([ts[-1] for ts in tses.values()])

log.info("T_MIN %s" % t_min)
log.info("T_MAX %s" % t_max)

signals = []
labels = list(streams.keys())
log.info("LABELS %s" % labels)
for label in labels:
    log.info(label)
    ts = tses[label]
    values = [d[label] if label in d else None for d in streams[label]]
    values = sp.remove_shots(values, nones=True)  # repair missing values
    signal = sp.resample(ts, values)
    num_samples = len(signal)
    sample_rate = num_samples / duration
    signal = sp.normalize(signal)
    signal = sp.smooth(signal, 15)
    signals.append(signal)    

log.info("Drawing...")
ctx = drawing.Context(1200, 500, margin=20, hsv=True)
for i, signal in enumerate(signals):
    color = i / len(signals), .8, .8, 1.
    ctx.plot(signal, stroke=color, thickness=2)
    ctx.line(10 / ctx.width, 1 - ((10 + (i * 10)) / ctx.height), 30 / ctx.width, 1 - ((10 + (i * 10)) / ctx.height), stroke=color, thickness=2)
    ctx.label(35 / ctx.width, 1 - ((13 + (i * 10)) / ctx.height), labels[i].upper(), size=8)            

ctx.output("charts/")
