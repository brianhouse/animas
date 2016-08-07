#!/usr/bin/env python3

import json
import numpy as np
import signal_processing as sp
from sklearn import manifold, decomposition, cluster
from housepy import config, log, util, drawing
from colors import colors

points = util.load("data/1470432105.pkl")
log.info("INPUT: %s POINTS, %s DIMENSIONS" % points.shape)
# points = manifold.Isomap().fit_transform(points)
# points = manifold.LocallyLinearEmbedding(method="modified").fit_transform(points)
# points = manifold.SpectralEmbedding().fit_transform(points)
# points = manifold.MDS().fit_transform(points)
# points = manifold.TSNE(n_iter=2000).fit_transform(points)
# points = decomposition.PCA(n_components=2).fit_transform(points)
# points = manifold.TSNE().fit_transform(points)
points = decomposition.PCA(n_components=2).fit_transform(points)
log.info("OUTPUT: %s POINTS, %s DIMENSIONS" % points.shape)

# labels = cluster.DBSCAN(eps=0.1, min_samples=5).fit_predict(points)
clusterer = cluster.KMeans(n_clusters=8)
labels = clusterer.fit_predict(points)
centroids = clusterer.cluster_centers_
labels += abs(min(labels))
max_label = max(labels)
log.info("CENTROIDS\n%s" % centroids)

cxs = sp.normalize(centroids[:,0], min(points[:,0]), max(points[:,0]))
cys = sp.normalize(centroids[:,1], min(points[:,1]), max(points[:,1]))

xs = sp.normalize(points[:,0])
ys = sp.normalize(points[:,1])

ctx = drawing.Context(500, 500)#, hsv=True)

for i in range(len(xs)):
    pos = i / len(xs)
    # ctx.arc(xs[i], ys[i], 2/ctx.width, 2/ctx.height, thickness=0.0, fill=(0.35 + (pos * 0.65), 1.0, 1.0))
    ctx.arc(xs[i], ys[i], 2/ctx.width, 2/ctx.height, thickness=0.0, fill=colors[labels[i]])
    # if i == 0:
    #     continue
    # ctx.line(xs[i], ys[i], xs[i-1], ys[i-1], stroke=(0.35 + (pos * 0.65), 1.0, 1.0))

# yeah, see -- how can you reduce it now?
for i in range(len(cxs)):
    ctx.arc(cxs[i], cys[i], 2/ctx.width, 2/ctx.height, thickness=5.0)

# for i in range(100):
#     pos = i / 100
#     ctx.arc(pos, 20 / ctx.width, 3/ctx.width, 3/ctx.height, thickness=0.0, fill=(0.35 + (pos * 0.65), 1.0, 1.0))

ctx.output("charts/")


## fix this please so that you dont split the numpy axes and just do it together
