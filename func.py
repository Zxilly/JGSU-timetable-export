import datetime
import hashlib
import json


def strHash(hash_string: str):
    return hashlib.md5(hash_string.encode()).hexdigest()


def dictHash(hash_dict: dict):
    return hashlib.md5(str(hash_dict).encode()).hexdigest()


def showData(data):
    print(json.dumps(data, ensure_ascii=False))
    exit(0)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.timedelta):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)
