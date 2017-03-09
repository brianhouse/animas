#!/usr/bin/env python3

import os
from housepy import server, config, log, process
from sampler import sample

process.secure_pid(os.path.join(os.path.dirname(__file__), "run"))

METALS = 'iron', 'aluminum', 'copper', 'lead'

class Home(server.Handler):

    def get(self, page=None):
        if page in METALS:
            point = sample()
            level = point[METALS.index(page)]
            level = int((level * 90) + 10) / 100.0  # .1 - 1.
            log.info("%s: %s" % (page, level))
            # return self.text(str(level))
            return self.text(str(1.0))
        return self.text("ANIMAS: %s" % (METALS,))

handlers = [
    (r"/?([^/]*)", Home),
]    

server.start(handlers)