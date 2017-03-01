#!/usr/bin/env python3

import json, datetime
import numpy as np
import signal_processing as sp
from housepy import config, log, timeutil, strings
from sklearn import manifold, decomposition, cluster
from mongo import db, DESCENDING

def sample(draw=False):
    log.info("START SAMPLE")
    # get the time
    # dt = timeutil.get_dt(tz=config['tz'])
    # dt -= datetime.timedelta(days=300)  # time adjustment if necessary for testing
    # t_utc = timeutil.t_utc(dt)
    t_utc = timeutil.t_utc()
    log.info(timeutil.get_string(t_utc, tz=config['tz']))

    # pull the last 24 hours
    log.info(config['sites'][config['sample']])
    query = {'site': config['sample'], 't_utc': {'$gt': t_utc - 86400, '$lt': t_utc}} 
    log.info(query)
    results = db.entries.find(query)
    results = list(results)
    log.info("%s results" % len(results))   # should be 96
    log.info(json.dumps(results[0], indent=4, default=lambda d: str(d)))

    # resample signals for each 
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
        except KeyError as e:
            log.error(log.exc(e))
            log.error(values)

    # draw if desired
    if draw:
        from housepy import drawing
        ctx = drawing.Context(1200, 500, margin=20, hsv=True)
        for i, label in enumerate(labels):
            color = i / len(labels), .8, .8, 1.
            signal = signals[i]
            ctx.plot(signal, stroke=color, thickness=2)
        ctx.output("charts/")        

    # collapse into n-dimensional points
    points = []
    for i in range(len(signals[0])):
        point = [signal[i] for signal in signals]
        points.append(point)

    # PCA to 4D
    points = np.array(points)
    log.info("INPUT: %s POINTS, %s DIMENSIONS" % points.shape)
    points = decomposition.PCA(n_components=4).fit_transform(points)
    log.info("OUTPUT: %s POINTS, %s DIMENSIONS" % points.shape)

    # normalize each dimension independently
    points = np.column_stack((sp.normalize(points[:,0], np.min(points[:,0]), np.max(points[:,0])), sp.normalize(points[:,1], np.min(points[:,1]), np.max(points[:,1])), sp.normalize(points[:,1], np.min(points[:,1]), np.max(points[:,2])), sp.normalize(points[:,2], np.min(points[:,3]), np.max(points[:,3]))))

    # use the last point
    point = list(points[-1])

    log.info("RESULT: %s" % point)

    return point

if __name__ == "__main__":
    sample(True)