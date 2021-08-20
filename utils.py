import os
from shutil import rmtree
from datetime import datetime
from time import mktime


def date2unix(date):
    date, time = date.split()
    hour, minutes = [int(s) for s in time.split(":")]
    return int(mktime(datetime.strptime(date, "%d/%m/%Y").timetuple())) + int(minutes*60) + int(hour*60*60)

def mkdir(path, clear_dirs):
    if os.path.exists(path):
        if clear_dirs:
            rmtree(path)
            os.makedirs(path)
            print("clear and create: {}".format(path))
            return True
        else:
            print("path exists, do nothing: {}".format(path))
            return False
    else:
        os.makedirs(path)
        print("create new path: {}".format(path))
        return True
