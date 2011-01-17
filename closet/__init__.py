# -*- coding: utf-8 -*-

import types
import riak

#temporary fix to use dev micromodels
import sys
sys.path.append('/home/eric/Projects/micromodels')
import micromodels

class RiakConnection(riak.RiakClient):

    def register_model(self, model):
        bucket_name = getattr(model, 'bucket', False) or model.__name__.lower()
        model.bucket = self.bucket(bucket_name)
        return model


class RiakModelList(object):

    def __init__(self, result_cls, query):
        self.query = query
        self.result_cls = result_cls

        for key in ('__getindex__', '__bool__', '__len__'):
            setattr(self, key,
                    lambda self, *args: getattr(s.results, key)(*args))

    @property
    def results(self):
        if not hasattr(self, '_cache'):
            self._cache = [self.result_cls(_key=k, **v) for k,v in self.query.run()]
        return self._cache


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
            self.__init__(_key=self._key, **self._lazy.get_data())
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
        return cls(_key=key, _lazy=cls.bucket.get(key))

    @classmethod
    def search(cls, query):
        query_object =  cls.bucket._client.search(cls.bucket._name, query)
        return RiakModelList(cls, query_object)

    @classmethod
    def map(cls, js_func):
        query_object = cls.bucket._client.add(cls.bucket._name).map(js_func)
        return RiakModelList(cls, query_object)

    def store(self):
        if not self._key:
            raise Exception("'User' object must have key to be stored")
        self.__class__.bucket.new(self._key, self.to_dict(serial=True)).store()