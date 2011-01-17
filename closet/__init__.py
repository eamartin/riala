# -*- coding: utf-8 -*-

import types
import riak

#temporary fix to use dev micromodels
import sys
sys.path.append('/home/eric/Projects/micromodels')
import micromodels

class RiakConnection(riak.RiakClient):

    def register_model(self, model):
        bucket_name = getattr(model, 'bucket') or model.__name__.lower()
        model.bucket = self.bucket(bucket_name)


class RiakModelList(object):

    def __init__(self, result_cls, query):
        self.query = query
        self.result_cls = result_cls

        for key in ('__getindex__', '__bool__', '__len__'):
            setattr(self, key, lambda self, *args: getattr(s.results, key)(*args))

    @property
    def results(self):
        if not hasattr(self, '_cache'):
            self._cache = [self.result_cls(k, **v) for k,v in self.query.run()]
        return self._cache


class RiakModel(micromodels.Model):
    '''Closets are a place to store your messy data.'''

    def __init__(self, key=None, _lazy=None, **kwargs):
        self.key = key
        self._lazy = _lazy
        if not self._lazy:
            super(RiakModel, self).__init__(kwargs)

    def __getattr__(self, name):
        if self._lazy:
            self.__init__(self.key, **self._lazy.get_data())
        return super(RiakModel, self).__getattr__(name)

    def set_key(self, key):
        self.key = key
        return self

    @classmethod
    def get(cls, key):
        return cls(key, lazy=cls.bucket.get(key))

    @classmethod
    def search(cls, query):
        query_object =  cls.bucket._client.search(cls.bucket._name, query)
        return RiakModelList(cls, query_object)

    @classmethod
    def map(cls, js_func):
        query_object = cls.bucket._client.add(cls.bucket._name).map(js_func)
        return RiakModelList(cls, query_object)

    def store(self):
        self.bucket.new(self.key, self.to_dict(serial=True)).store()