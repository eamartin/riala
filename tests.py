# -*- coding: utf-8 -*-

from attest import Tests, Assert
from riala import RiakConnection, RiakModel
from micromodels import *

init = Tests()
mock_connection = Tests()

class User(RiakModel):
    name = CharField()
    age = IntegerField()

data = {
    'eric': dict(name='Eric M.', age=18),
    'jordan': dict(name='Jordan C.', age=17),
    'bobby': dict(name='Bobby L.', age=50)
}


@init.test
def full_init():
    key = data.keys()[0]
    instance = User(**data[key])
    Assert(instance.to_dict()) == data[key]

@init.test
def late_init():
    key = data.keys()[0]

    instance = User()
    Assert(instance.to_dict()) == {}

    instance.name = data[key]['name']
    Assert(instance.to_dict()['name']) == data[key]['name']

    instance.age = data[key]['age']
    Assert(instance.to_dict()['age']) == data[key]['age']

    instance.set_data(data[key])
    Assert(instance.to_dict()) == data[key]

conn = RiakConnection()
conn.register(User)

@mock_connection.test
def test_get():
    instance = User.get(key)

    Assert(instance._lazy).is_not(None)
    Assert(instance.to_dict()) == data
    Assert(instance.name) == data['name']
    Assert(instance._lazy).is_(None)

@mock_connection.test
def test_map(User, key):
    all_users = User.map(
    '''function(v)
    {
        var data = JSON.parse(v.values[0].data);
        return [[v.key, data]];
    }''')

    iter(all_users)
    len(all_users)
    all_users[0], all_users[-1], all_users[1:-1]
    bool(all_users)

tests = Tests([init, mock_connection])

if __name__ == '__main__':
    tests.main()