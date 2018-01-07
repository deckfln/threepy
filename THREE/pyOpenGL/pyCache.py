"""
Cache object as pickles
"""
import pickle
import os.path
import os


class pyCache:
    def __init__(self, file):
        self.fcached = "cache/%s" % file.replace("/", "-")
        self.file = file
        self.obj = None

        if not os.path.exists("cache"):
            os.mkdir("cache")

    def load(self):
        # if cached file doesn't exist
        if not os.path.isfile(self.fcached):
            return None

        # if cached file is older than the source file
        if os.path.getmtime(self.file) > os.path.getmtime(self.fcached):
            return None

        # cache is uptodate
        with open(self.fcached, "rb") as f:
            self.obj = pickle.load(f)

        return self.obj

    def save(self, obj):
        with open(self.fcached, "wb") as f:
            pickle.dump(obj, f)