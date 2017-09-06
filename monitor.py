# -*- coding: utf-8 -*-



class AppMonitor(object):
    def __init__(self, app, event, params):
        self.__app = app
        self.__event = event
        self.__params = params
        self.__events = {
            "config.update": self.update_config,
            "code.update": self.update_code,
        }

    def __call__(self):
        try:
            return self.__events[self.__event](self.__params)
        except Exception, e:
            return False, "{}执行错误:{}".format(self.__event, e.message)

    def update_config(self, params):
        for name, cfg in params.iteritems():
            k, v = cfg.popitem()
            if name == "main":
                __d = self.__app.main
            elif name == "redis":
                __d = self.__app.redis
            elif name == "code":
                __d = self.__app.code
            elif name == "node":
                __d = self.__app.node
            else:
                __d = object

            print __d.__dict__
            setattr(__d, k, v)
        else:
            return True, None

    def update_code(self, params):
        for name, cfg in params.iteritems():
            self.__app.update_package(name, **cfg)
        else:
            return True, None

