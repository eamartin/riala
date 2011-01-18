# -*- coding: utf-8 -*-

from attest import Tests, Assert
from closet import RiakConnection, RiakModel
from micromodels import *

no_connection = Tests()
connection_required = Tests()

class User(RiakModel):
    name = CharField()
    age = IntegerField()

data = dict(name='Eric Martin', age=18)

@no_connection.test
def full_init():
    instance = User(**data)
    Assert(instance.to_dict()) == data

@no_connection.test
def late_init():
    instance = User()
    Assert(instance.to_dict()) == {}
    instance.name = data['name']
    Assert(instance.to_dict()) == dict(name=data['name'])
    instance.age = data['age']
    Assert(instance.to_dict()) == data

@connection_required.context
def make_context():
    RiakConnection(port=8091).register(User)
    key = 'eric'
    User(_key=key, **data).store()
    yield User, key

@connection_required.test
def test_get(User, key):
    instance = User.get(key)
    Assert(instance._lazy).is_not(None)
    Assert(instance.to_dict()) == data
    Assert(instance.name) == data['name']
    Assert(instance._lazy).is_(None)

@connection_required.test
def test_map(User, key):
    all_users = User.map(
    '''function(v)
    {
        var data = JSON.parse(v.values[0].data);
        return [[v.key, data]];
    }''')

    for user in all_users:
        print user.to_dict()

    print len(all_users)

tests = Tests([no_connection, connection_required])

if __name__ == '__main__':
    tests.main()