# -*- coding: utf-8 -*-

from attest import Tests, Assert
from closet import Drawer
from micromodels import *

closet = Tests()

@closet.context
def context():
    class User(Drawer):
        name = CharField()
        age = IntegerField()
    yield User, dict(name='Eric Martin', age=18)


@closet.test
def full_init(User, data):
    instance = User(**data)
    Assert(instance.to_dict()) == data

@closet.test
def late_init(User, data):
    instance = User()
    Assert(instance.to_dict()) == {}
    instance.name = data['name']
    Assert(instance.to_dict()) == dict(name=data['name'])
    instance.age = data['age']
    Assert(instance.to_dict()) == data

if __name__ == '__main__':
    closet.main()