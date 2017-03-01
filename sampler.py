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
    dt = timeutil.get_dt(t_utc, tz=config['tz'])
    log.info("CURRENT TIME %s" % timeutil.get_string(t_utc, tz=config['tz']))

    # pull the last 24 hours worth -- we're going to normalize over that to set our dynamic levels
    log.info(config['sites'][config['sample']])

    # # this is the real-time last 24 hours
    # query = {'site': config['sample'], 't_utc': {'$gt': t_utc - 86400, '$lt': t_utc}}     
    # log.info(query)
    # results = db.entries.find(query)

    # this is the last 24 hours we have
    # assume updating every 15 minutes, last 24 hours is the last 96 results
    results = db.entries.find({'site': config['sample']}).sort([('t_utc', DESCENDING)]).limit(96)    
    results = list(results)
    results.reverse()
    log.info("%s results" % len(results))   # should be 96
    log.info(json.dumps(results[-1], indent=4, default=lambda d: str(d)))   # show the last one

    # resample signals for each 
    ts = [d['t_utc'] for d in results]
    duration = ts[-1] - ts[0]
    log.info("DURATION %s %s" % (duration, timeutil.format_seconds(duration)))
    signals = []
    rates = []
    labels = list(config['labels'].values())
    labels.sort()
    for i, label in enumerate(labels):
        # log.debug(label)
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

    # PCA to 4D -- this takes whatever data we've got and maximizes variation for our four panels
    points = np.array(points)
    # log.debug("INPUT: %s POINTS, %s DIMENSIONS" % points.shape)
    points = decomposition.PCA(n_components=4).fit_transform(points)
    # log.debug("OUTPUT: %s POINTS, %s DIMENSIONS" % points.shape)

    # normalize each dimension independently, again amplifying dynamics
    points = np.column_stack((sp.normalize(points[:,0], np.min(points[:,0]), np.max(points[:,0])), sp.normalize(points[:,1], np.min(points[:,1]), np.max(points[:,1])), sp.normalize(points[:,1], np.min(points[:,1]), np.max(points[:,2])), sp.normalize(points[:,2], np.min(points[:,3]), np.max(points[:,3]))))

    # now, for each time this is queried we want to return an interpolation between the last two points
    # this essentially implements a delay that closes in on the most recent query
    # ...hopefully to be refreshed with a new USGS reading when it gets there
    # if that reading doesnt come, it's ok, it just hovers there until we proceed
    # aaandd actually we want a couple of hours delay, because these come in at bulk every 1-4 hours

    # we know we have 96 points. four hours back is 16 points
    # interpolating between points -17 and -16 should give the most recent guaranteed smooth transitions
    # transduction takes time, pues

    point_a = points[-17]
    point_b = points[-16]
    # log.debug(point_a)
    # log.debug(point_b)
    
    # linear interpolation over 15 minutes
    position = (((dt.minute % 15) * 60) + dt.second) / (15 * 60)
    # log.debug(position)
    point = [(point_a[i] * (1.0 - position)) + (point_b[i] * position) for i in range(len(point_a))]

    log.info("RESULT: %s" % point)

    return point

if __name__ == "__main__":
    sample(True)