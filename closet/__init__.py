# -*- coding: utf-8 -*-

import riak

#temporary fix to use dev micromodels
import sys
sys.path.append('/home/eric/Projects/micromodels')
import micromodels


class Drawer(micromodels.Model):
    '''Closets are a place to store your messy data.'''

    def __init__(self, **kwargs):
        super(Drawer, self).__init__(kwargs)
