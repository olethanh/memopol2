from django.conf import settings
from couchdbkit import Server, ResourceNotFound

NONDICT_WRAP_MAGIC = "couchcfg-value"

class CouchCfg(object):
    """
    A simple couchdb wrapper to store and retrieve values (or objects) with no fuss
    """

    def __init__(self, couch_db_uri, couch_db_name):
        self.server = Server(couch_db_uri)
        self.db = self.server.get_or_create_db(couch_db_name)

    def set(self, name, value):
        """
        sets the given key to the given value. if value is a dict, store it directly. if not, wrap it into a dict.
        """

        try:
            del self.db[name]
        except ResourceNotFound:
            pass
        if isinstance(value, dict):
            self.db[name] = value
        else:
            self.db[name] = { NONDICT_WRAP_MAGIC: value }

    def get(self, name, default=None):
        """
        returns the value of the given key, or the default value in case the resource is not found in couchdb.
        will unwrap non-dict values stored with set()
        """

        try:
            val = self.db[name]
        except ResourceNotFound:
            val = default
        # alternatively, return (val is None and None) or (isinstance(val, dict) and val.get(NONDICT_WRAP_MAGIC, val)) or val
        if val is None:
            return None
        if isinstance(val, dict):
            return val.get(NONDICT_WRAP_MAGIC, val)
        return val
    
    def remove(self, name):
        del self.db[name]

# create a singleton (FIXME)
CouchCfg = couchcfg = CouchCfg(settings.COUCHDB, "cfg")
