#!/bin/bash

#mojo-webqq 的插件 openqq 提供了一个 http 接口，故可以利用它实现定时探测，以探测 qq 是否还在线

curl -XPOST -H"Content-Type: application/json" https://yourself.com/qqapi/upwarning/ -d '{"upid": '200', "content": "I am alive!"}'
