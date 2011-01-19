from riala import *

conn = RiakConnection(port=8091)

@conn.register
class User(RiakModel):
    bucket = 'users'

    name = micromodels.CharField()
    age = micromodels.IntegerField()

all = User.map(
    '''function(v)
    {
        var data = JSON.parse(v.values[0].data);
        return [[v.key, data]];
    }''')
