#第一行
#this is 127
import redis
import json
rd = redis.Redis(host='192.168.1.101', port=6379, db=6)
key_ = 'validateCode:user:{0}'.format(15090658127)
if rd.exists(key_):
    js = json.loads(rd.get(key_))
    print('\n手机登录验证码:\t', js['code'])
    print('111')