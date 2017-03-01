#!/usr/bin/env python3

import json, time
import numpy as np
import signal_processing as sp
from sklearn import manifold, decomposition, cluster
from housepy import config, log, util, chart

# points, rates = util.load("data/1470432105.pkl")   # last week
# points, rates = util.load("data/1470593687.pkl")   # last two weeks
# points, rates = util.load("data/1470681705.pkl")   # smoothed!
# points, rates = util.load("data/1470681860.pkl")   # not smoothed!
points, rates = util.load("data/last_snap.pkl")
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

centroids = np.column_stack((sp.normalize(centroids[:,0], np.min(points[:,0]), np.max(points[:,0])), sp.normalize(centroids[:,1], np.min(points[:,1]), np.max(points[:,1]))))
points = np.column_stack((sp.normalize(points[:,0], np.min(points[:,0]), np.max(points[:,0])), sp.normalize(points[:,1], np.min(points[:,1]), np.max(points[:,1]))))



chart.plot(points, sample_axis=True, scatter=False, c=(0., 0., 1., 1.), linewidth=2)
chart.plot(centroids, sample_axis=True, scatter=True, c=(1., 0., 0., 1.), linewidth=0, s=100)

chart.show("charts/")

