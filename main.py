#!/usr/bin/env python3

from housepy import server

class Home(server.Handler):

    def get(self, page=None):
        if page == "iron":
            return self.text("iron")
        if page == "aluminum":
            return self.text("aluminum")
        if page == "copper":
            return self.text("copper")
        if page == "lead":
            return self.text("lead")
        return self.text("OK")

handlers = [
    (r"/?([^/]*)", Home),
]    

server.start(handlers)