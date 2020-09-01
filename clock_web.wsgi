activate_this = "/var/www/flask/flask_env/bin/activate_this.py"
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, "/var/www/flask/PythonTimeClock_Flask_WebApp/")

from webtime import app as application