# -*- coding: utf-8 -*-
import inspect
import logging
import sys
from os import listdir
from os.path import dirname as f_dir, splitext

from monkey.plugins import singleton


@singleton
class RemoteCode(object):
    def __init__(self, redis_client=None, code_name=None):
        self.redis_client = redis_client
        self.code_name = code_name
        self.__code_obj = {}
        self.log = logging.getLogger("RemoteCode")

    def __e(self, name, source):
        exec source
        __c = eval(name)
        setattr(__c, "package", self.package)
        setattr(__c, "packages", self.packages)
        return __c

    def __package(self, name):
        if self.__code_obj.get(name) and not self.__code_obj[name].get("had_changed"):
            return self.__code_obj[name]['obj']

        __s = self.redis_client.hget(self.code_name, name)
        if not __s:
            self.log.error(u"{}不存在".format(name))
            return

        __obj = self.__e(name.split(".")[-1], __s)

        self.__code_obj[name] = {"had_changed": False, "obj": __obj}

        return __obj

    def __packages(self, names):
        for name, _code in zip(names, self.redis_client.hmget(self.code_name, *names)):
            if not _code:
                self.log.error(u"{}不存在".format(name))
                continue

            if not self.__code_obj.get(name):
                self.__code_obj[name] = {"had_changed": False, "obj": None}
            elif not self.__code_obj[name].get("had_changed"):
                yield name, self.__codes[name]["obj"]

            exec _code

            __c = eval(name.split(".")[-1])
            setattr(__c, "import_package", self.package)
            setattr(__c, "import_packages", self.packages)
            yield name, __c

    def update(self, name, **kwargs):
        if name not in self.__code_obj:
            return False, "can not find {}".format(name)
        self.__code_obj[name].update(kwargs)
        return True, self.__package(name)

    def package(self, name):
        return self.__package(name)

    def packages(self, names):
        return self.__packages(names)

    def get_all_packages(self):
        return self.redis_client.hkeys(self.code_name)


def code_register(redis_client=None, code="__code__", **kwargs):
    for name, f_source in get_codes():
        redis_client.hset(
            code,
            name,
            f_source
        )


def get_codes():
    f_path = f_dir(__file__)
    sys.path.append(f_path)

    for f in listdir(f_path):
        name, f_ext = splitext(f)

        if name in ["__init__", "__main__"] or f_ext in ['.pyc', '.pyd', 'pyx']:
            continue

        __obj = __import__(name)
        for k, v in inspect.getmembers(__obj):
            if v.__class__.__name__ == 'type':
                yield "{}.{}".format(name, k), "# -*- coding: utf-8 -*-\n\n\n" + inspect.getsource(v)
