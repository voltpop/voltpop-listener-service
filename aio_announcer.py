from aiohttp import web
import argparse
import codecs
import datetime
import json
import os
import pickle
import redis
import yaml
import sqlite3

class Announcer(object):
    def __init__(self):
        # Init / Configure the Flask app
        self.announcer = app = web.Application()
        routes = web.RouteTableDef()

        @routes.get('/query/{key}')
        async def query_example(request):
            key = str(request.rel_url).split('/')[-1]
            print("Querying for %s" % key)
            if key in config['announcer'].keys() and config['announcer'][key]["queryable"]:
                return web.Response(text="{}".format(self.queryAnnouncement(key)))

        @routes.post('/announce/{key}')
        async def announce(request):
            key = str(request.rel_url).split('/')[-1] 
            if key in config['announcer'].keys():
                q = config['announcer'][key]
                if q['security'] and q['token_string'] is not None:
                    allowed = False
                    if request.headers.get('SecureToken') == q['token_string']:
                        allowed = True
                    else:
                        allowed = False
                elif not q['security']:
                    allowed = True
                else:
                    raise web.HTTPInternalServerError()
                
                if allowed:
                    async for line in request.content:
                        web.Response(text=line.decode('utf8'))
                    self.stashAnnouncement([datetime.datetime.now().isoformat(), key, str(request)])

        app.add_routes(routes)

        # Initialize the Announcement Stash
        self.dbfile = config["dbfile"]
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()

        db.execute("""CREATE TABLE IF NOT EXISTS main.data (
            id INTEGER PRIMARY KEY,
            datetime TEXT NOT NULL,
            key TEXT NOT NULL,
            payload BLOB NOT NULL);""")
        db_con.commit()
        db_con.close()


    def queryAnnouncement(self, key):
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        output = db.execute("SELECT * FROM main.data WHERE key=:rediskey", {"rediskey": key})
        return(output.fetchall())

    def stashAnnouncement(self, values):
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        db.execute("INSERT INTO main.data (id, datetime, key, payload) VALUES (NULL, ?, ?, ?)", values)
        db_con.commit()
        db_con.close()

    def start(self):
        web.run_app(self.announcer, host='127.0.0.1', port=os.environ['VPA_WEBHOST_PORT'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VoltPop Redis PubSub Target")
    parser.add_argument('--debug', action='store_true', default=False)
    config = yaml.load(open("announcer.yml", "r"), Loader=yaml.SafeLoader)
    a = Announcer()
    a.start()
