# -*- coding: utf-8 -*-
import sqlite3
import time
from collections import OrderedDict
from flask import Flask, g, render_template, request, make_response
from flask_bootstrap import Bootstrap

PAGESIZE = 50
INTERVAL_MENU = [
    ('1', '24 hours'),
    ('3', 'Three days'),
    ('7', 'One week'),
    ('14', 'Two weeks'),
    ('28', 'Four weeks')
    ]
INTERVAL_MENU_DICT = {k: v for (k,v) in INTERVAL_MENU}
SYSFILE_MENU = [
    ('0', 'system pages excluded'),
    ('1', 'system pages included'),
    ('2', 'system pages only')
    ]
SYSFILE_MENU_DICT =  {k: v for (k,v) in SYSFILE_MENU}
SQL_Q = {
    '0': "SELECT url, title, count(timestamp) FROM edits WHERE timestamp >= ? AND is_system = 0 GROUP BY url ORDER BY count(timestamp) DESC",
    '1': "SELECT url, title, count(timestamp) FROM edits WHERE timestamp >= ? GROUP BY url ORDER BY count(timestamp) DESC",
    '2': "SELECT url, title, count(timestamp) FROM edits WHERE timestamp >= ? AND is_system = 1 GROUP BY url ORDER BY count(timestamp) DESC"
    }

app = Flask(__name__)
Bootstrap(app)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        DBFILE = '/var/www/enwiki/data/wikiedits.db'
        db = g._database = sqlite3.connect(DBFILE)
    return db


def get_cursor():
    db = get_db()
    return db.cursor()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status')
def status():
    c = get_cursor()
    c.execute("SELECT MAX(timestamp) FROM edits")
    q = c.fetchone()
    c.close()
    res = time.time() - q[0]
    return "{} seconds since last recorded edit".format(int(res))


@app.route('/_data')
def data():
    interval = request.args.get('t') if request.args.get('t') is not None else request.cookies.get('t') if request.cookies.get('t') is not None else "7"
    sysfile = request.args.get('s') if request.args.get('s') is not None else request.cookies.get('s') if request.cookies.get('s') is not None else "0"
    c = get_cursor()
    timelimit = time.time() - int(interval)*24*60*60
    c.execute(SQL_Q[sysfile], (timelimit,))
    q = c.fetchmany(size=PAGESIZE)
    c.close()
    res = [[id + 1, url, title, count] for id, (url, title, count) in enumerate(q)]
    resp = make_response(render_template('table.html',res=res,interval_menu=INTERVAL_MENU,interval=interval,
            interval_text=INTERVAL_MENU_DICT[interval], sysfile_menu=SYSFILE_MENU,
            sysfile=sysfile, sysfile_text=SYSFILE_MENU_DICT[sysfile]))
    resp.set_cookie('t', interval)
    resp.set_cookie('s', sysfile)
    return resp


@app.route('/_stats')
def stats():
    c = get_cursor()
    c.execute("SELECT MIN(timestamp) FROM edits")
    oldest = c.fetchone()[0]
    hours = (time.time() - oldest) // (3600) 
    minutes = (time.time() - oldest) // (60) 
    days = hours // 24
    c.execute("SELECT COUNT(*) FROM edits")
    num = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM edits WHERE is_system = 1")
    num_sys = c.fetchone()[0]
    c.close()
    res = 'In the last {} days, there were a total of {:,d} edits.'.format(int(days), num) + '<br />'
    res += 'That\'s an average of {:.1f} edits an hour or {:.1f} a minute.'.format(float(num/hours), float(num/minutes)) + '<br />'
    res += 'Of those, {:,d} were system page edits ({:.1f} percent).'.format(num_sys, num_sys * 100.0 / num)
    return res



if __name__ == '__main__':
    app.run()