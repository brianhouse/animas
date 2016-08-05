#!/usr/bin/env python3

import json
import numpy as np
import signal_processing as sp
from housepy import config, log, util, drawing

points = util.load("data/1470432105.pkl")

for point in points:
    print(point)

