import time
import sqlite3
import logging


def clean():
    logging.basicConfig(filename='/var/www/enwiki/logs/log.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
    db = sqlite3.connect('/var/www/enwiki/data/wikiedits.db')
    cursor = db.cursor()
    timelimit = time.time() - 28*24*60*60
    cursor.execute("DELETE FROM edits WHERE timestamp <= ?", (timelimit,))
    count = cursor.rowcount
    db.commit()
    logging.info('cleand db, {} rows deleted'.format(count))


if __name__ == '__main__':
    clean()