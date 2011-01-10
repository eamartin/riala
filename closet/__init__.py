# -*- coding: utf-8 -*-

import functools
import riak

#temporary fix to use dev micromodels
import sys
sys.path.append('/home/eric/Projects/micromodels')
import micromodels

class RiakConnection(riak.RiakClient):

    def register_model(self, model):
        bucket_name = getattr(model, 'bucket') or model.__name__.lower()
        model.bucket = self.bucket(bucket_name)


class LazyQuery(object):

    getter_methods = {
                        riak.RiakObject: 'get_data',
                        riak.RiakMapReduce: 'run',
    }

    def __init__(self, query):
        self.query = query

    def __call__(self):
        return getattr(self.query, getter_methods[type(self.query)]).__call__()

class RiakModel(micromodels.Model):
    '''Closets are a place to store your messy data.'''

    def __init__(self, **kwargs):
        super(RiakModel, self).__init__(kwargs)

    @classmethod
    def get(cls, key):
        return cls.bucket.get(key)

    @classmethod
    def search(cls, query):
        return cls.bucket._client.search(cls.bucket._name, query)

    @classmethod
    def map(cls, js_func):
        return cls.bucket._client.add(cls.bucket._name).map(js_func)

    def store(self, key):
        self.bucket.new(key, self.to_dict(serial=True)).store()