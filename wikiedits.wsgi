activate_this = '/home/bronek/.virtualenvs/enwiki/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, '/home/bronek/dev/enwiki')

from wikiedits import app as application