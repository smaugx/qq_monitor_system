#!/usr/bin/env pyhon
#-*- coding:utf-8 -*-

import redis

spool = redis.ConnectionPool(host='127.0.0.1', port=6380)
r = redis.StrictRedis(connection_pool = spool)


#自定义的 myid 与 name 的对应关系，用来区别给什么对象上传后发送报警信息;规定三位数 id，好友以 1 开头,群以 2开头,讨论组以 3 开头;update: 作为元数据，插入到 redis，每次从 redis 拿数据，这样添加分组后就不用重启该脚本了
MyidName  = {
    0:'Myself',
    100:'史矛革',
    #101:'好友xxx',
    201:'兄弟两',
    #201:'群xxx',
    211:'DNS监控报警',
    }


redis_qq_user_idname = "qq:user-defined-idname"

for (_id,_name) in MyidName.items():
  r.hset(redis_qq_user_idname,_id,_name)
