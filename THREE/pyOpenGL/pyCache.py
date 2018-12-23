"""
Cache object as pickles
"""
import pickle
import os.path
import os


class pyCache:
    def __init__(self, cwd, file):
        self.fcached = cwd+"/cache/%s" % file.replace("/", "-").replace(":", "-")
        self.file = file
        self.obj = None

        if not os.path.exists(cwd + "/cache"):
            os.mkdir(cwd + "/cache")

    def load(self, force=False):
        # if cached file doesn't exist
        if not os.path.isfile(self.fcached):
            return None

        # if cached file is older than the source file
        if not force and os.path.getmtime(self.file) > os.path.getmtime(self.fcached):
            return None

        # cache is up to date
        with open(self.fcached, "rb") as f:
            self.obj = pickle.load(f)

        return self.obj

    def save(self, obj):
        with open(self.fcached, "wb") as f:
            pickle.dump(obj, f)
