#!/bin/bash

curl -XPOST -H"Content-Type: application/json" https://iruka.upyun.com/qqapi/upwarning/ -d '{"upid": '200', "content": "I am alive!"}'
