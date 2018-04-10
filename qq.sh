#!/bin/bash

check_qq=`ps -ef |grep mojo_webqq_login.pl |grep -v grep | awk '{print $2}'`

if [  $check_qq ] ; then
echo "qq is alive,pid is ${check_qq}"
kill -9 $check_qq
echo "kill qq"
fi

nohup /usr/local/bin/perl  /root/qq_monitor_system/mojo_webqq_login.pl >> /root/qq_monitor_system/qq.log & 2>&1
echo "start qq"
