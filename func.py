import hashlib
import json
import datetime
def hash_func(hash_string:str):
    return hashlib.md5(hash_string.encode()).hexdigest()

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.timedelta):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)