# -*- coding: utf-8 -*-

import functools
import riak

#temporary fix to use dev micromodels
import sys
sys.path.append('/home/eric/Projects/micromodels')
import micromodels


class RiakConnection(riak.RiakClient):

    def register(self, model):
        bucket_name = getattr(model, 'bucket', False) or model.__name__.lower()
        model._bucket = self.bucket(bucket_name)
        return model


class RiakModelList(object):

    class __metaclass__(type):

        @staticmethod
        def make_closure(key):
            def wrapper(self, *args, **kwargs):
                func = getattr(self.results, key)
                return func(*args, **kwargs)

            wrapper.__name__ = key
            return wrapper

        def __init__(cls, name, bases, attrs):
            for key in ('__iter__', '__getitem__', '__bool__', '__len__'):
                setattr(cls, key, cls.make_closure(key))

    def __init__(self, result_cls, query):
        self.query = query
        self.result_cls = result_cls

    def reduce(self, js_func):
        self.query = self.query.reduce(js_func)
        return self

    @property
    def results(self):
        if not hasattr(self, '_cache'):
            self._cache = [self.result_cls(_key=k, **v) for k,v in self.query.run()]
        return self._cache

    def to_list(self, serial=False):
        return [r.to_dict(serial=serial) for r in self.results]


class RiakModel(micromodels.Model):
    '''Closets are a place to store your messy data.'''

    def __init__(self, _key=None, _lazy=None, **kwargs):
        super(RiakModel, self).__init__()
        self._lazy = _lazy
        self._key = _key
        if not self._lazy:
            self.set_data(kwargs)

    def __getattr__(self, name):
        if self._lazy:
            try:
                self.__init__(_key=self._key, **self._lazy.get_data())
            except TypeError:
                raise Exception("'%s' key does not exist in database" %
                                self._lazy.get_key())
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, name))

    def set_key(self, key):
        self._key = key
        return self

    @classmethod
    def get(cls, key):
        return cls(_key=key, _lazy=cls._bucket.get(key))

    @classmethod
    def search(cls, query):
        query_object =  cls._bucket._client.search(cls._bucket._name, query)
        return RiakModelList(cls, query_object)

    @classmethod
    def map(cls, js_func):
        query_object = cls._bucket._client.add(cls._bucket._name).map(js_func)
        return RiakModelList(cls, query_object)

    def store(self):
        if not self._key:
            raise Exception("'User' object must have key to be stored")
        self.__class__._bucket.new(self._key, self.to_dict(serial=True)).store()
        return self