#!/usr/bin/env python3

from housepy import server, config, log
from sampler import sample

METALS = 'iron', 'aluminum', 'copper', 'lead'

class Home(server.Handler):

    def get(self, page=None):
        if page in METALS:
            point = sample()
            level = point[METALS.index(page)]
            level = int(level * 100) / 100.0
            log.info("%s: %s" % (page, level))
            return self.text(str(level))
        return self.text("ANIMAS: %s" % (METALS,))

handlers = [
    (r"/?([^/]*)", Home),
]    

server.start(handlers)