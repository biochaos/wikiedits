from sseclient import SSEClient as EventSource
import json
import logging
import sys
import time
import sqlite3
from logging.handlers import RotatingFileHandler


system_names = {'media', 'special', 'talk', 'user', 'user talk', 'wikipedia', 'wikipedia talk', 'file', 'file talk', 
    'mediawiki', 'mediawiki talk', 'template', 'template talk', 'help', 'help talk', 'category', 'category talk',
    'portal', 'portal talk', 'book', 'book talk', 'draft', 'draft talk', 'education program', 'education program talk',
    'timedtext', 'timedtext talk', 'module', 'module talk', 'gadget', 'gadget talk', 'gadget definition', 
    'gadget definition talk'} #list from https://en.wikipedia.org/wiki/Wikipedia:Namespace

def main():
    #logging.basicConfig(filename='/home/bronek/dev/wiki/log.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
    handler = RotatingFileHandler(filename='/var/www/enwiki/logs/log.log',maxBytes=5*1024*1024,backupCount=1)
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s',handlers=[handler])
    logging.info('==================================')
    logging.info('building started')
    #connect to bd
    db = sqlite3.connect('/var/www/enwiki/data/wikiedits.db')
    cursor = db.cursor()
    try:
        cursor.execute("CREATE TABLE edits (url text, title text, timestamp real, is_system integer)")
        db.commit()           
        logging.info('created table')
    except Exception as e:
        logging.info(e)
        cursor.execute("SELECT count(*) FROM edits")
        res = cursor.fetchone()[0]
        logging.info('{} entries in table'.format(res))
    cursor.close()
    count = 0
    #connect to wiki edit stream
    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    for event in EventSource(url):
        if event.event == 'message' and event.data:
            e = json.loads(event.data)
            if e['wiki'] == 'enwiki' and e['type'] == 'edit' and e['title'].split('.')[-1].lower() not in {'jpeg' , 'jpg', 'gif', 'svg', 'png'}:
                is_system = 0
                if e['title'].split(':')[0].lower() in system_names:
                    is_system = 1
                # insert into db
                edit = (e['meta']['uri'], e['title'], e['timestamp'], is_system)
                #cursor = db.cursor()
                #cursor.execute("INSERT INTO edits VALUES (?, ?, ?, ?)", edit)
                #db.commit()
                #cursor.close()
                try:
                    with sqlite3.connect('/var/www/enwiki/data/wikiedits.db') as d:
                        d.execute("INSERT INTO edits VALUES (?, ?, ?, ?)", edit)
                    count += 1
                except Error as e:
                    logging.info(e)
                if count % 1000 == 0:
                    logging.info('new edits: {}'.format(count))
        elif event.event == 'error':
            logging.info('--- Encountered error while building db:\n', event.data)


if __name__ == '__main__':
    main()