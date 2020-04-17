import logging
import shelve2
from os import makedirs
from os.path import join
import hashlib
from json import dump


logger = logging.getLogger(__name__)


class Db:
    def __init__(self, basedir, suffix):
        self.basedir = basedir
        self.db_path = join(basedir, "cache-{}".format(suffix))
        self.db = None
        self.hits = 0
        self.misses = 0
        makedirs(self.basedir, exist_ok=True)
        self.db = shelve2.open2(self.db_path)

    def _genkey(self, text):
        return hashlib.sha256(text.encode("utf8")).hexdigest()

    def add(self, key, data):
        self.db[self._genkey(key)] = data

    def remove(self, key):
        del self.db[self._genkey(key)]

    def get(self, key):
        genkey = self._genkey(key)
        if genkey in self.db:
            logger.debug("Cache hit for {}".format(key))
            self.hits += 1
            return (True, self.db[genkey])
        else:
            logger.debug("Cache miss for {}".format(key))
            self.misses += 1
            return (False, None)

    def stats(self):
        return dict(hits=self.hits, misses=self.misses)

    def __del__(self):
        with open(self.db_path + ".cache_stats.json", "w") as f:
            dump(self.stats(), f)
        self.db.close()
