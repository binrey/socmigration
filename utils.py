import os
from shutil import rmtree


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
