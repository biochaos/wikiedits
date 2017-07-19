import daemon
import logging
from logging.handlers import RotatingFileHandler
from build_db import main



with daemon.DaemonContext():
    while True:
        try:
            main()
        except Exception as e:
            handler = RotatingFileHandler(filename='/var/www/enwiki/logs/log.log',maxBytes=5*1024*1024,backupCount=1)
            logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s',handlers=[handler])
            logging.info('==================================')
            logging.info('ERROR')
            logging.info(e)
            logging.info('==================================')


