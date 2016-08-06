#!/usr/bin/env python3

import json
import numpy as np
import signal_processing as sp
from sklearn import manifold
from housepy import config, log, util, drawing

points = util.load("data/1470432105.pkl")
log.info("INPUT: %s POINTS, %s DIMENSIONS" % points.shape)

# points = manifold.Isomap().fit_transform(points)
# points = manifold.LocallyLinearEmbedding(method="modified").fit_transform(points)
# points = manifold.SpectralEmbedding().fit_transform(points)
# points = manifold.MDS().fit_transform(points)
points = manifold.TSNE(n_iter=2000).fit_transform(points)

log.info("OUTPUT: %s POINTS, %s DIMENSIONS" % points.shape)

xs = sp.normalize(points[:,0])
ys = sp.normalize(points[:,1])

ctx = drawing.Context(500, 500, hsv=True)

for i in range(len(xs)):
    pos = i / len(xs)
    ctx.arc(xs[i], ys[i], 2/ctx.width, 2/ctx.height, thickness=0.0, fill=(0.35 + (pos * 0.65), 1.0, 1.0))
    if i == 0:
        continue
    ctx.line(xs[i], ys[i], xs[i-1], ys[i-1], stroke=(0.35 + (pos * 0.65), 1.0, 1.0))

for i in range(100):
    pos = i / 100
    ctx.arc(pos, 20 / ctx.width, 3/ctx.width, 3/ctx.height, thickness=0.0, fill=(0.35 + (pos * 0.65), 1.0, 1.0))

ctx.output("charts/")



"""
http://scikit-learn.org/stable/modules/manifold.html

sklearn.manifold.Isomap(n_neighbors=5, n_components=2, eigen_solver='auto', tol=0, max_iter=None, path_method='auto', neighbors_algorithm='auto')[source]


"""