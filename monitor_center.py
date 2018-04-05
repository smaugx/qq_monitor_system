#!/usr/bin/env python
#-*- coding:utf-8 -*-

import requests
from flask import Flask ,request, url_for, render_template
import json
import urlparse
import urllib2

app = Flask(__name__)

openqq_url = 'http://127.0.0.1:5000/'

#mojo-webqq 登录后各个好友、群、讨论组 name 与 id 的对应关系
NameId     = {}

#自定义的 myid 与 name 的对应关系，用来区别给什么对象上传后发送报警信息;规定三位数 id，好友以 1 开头,群以 2开头,讨论组以 3 开头
MyidName  = {
    0:'Myself',
    100:'史矛革',
    101:'好友xxx',
    200:'兄弟两',
    201:'群xxx',
    }

#获取用户数据
def get_user_info():
  _url = urlparse.urljoin(openqq_url,'/openqq/get_user_info')
  _header = {'Content-Type':'application/json','Connection':'close'}


  myself = {}
  try:
     r = requests.get(_url ,headers = _header)
     if r.status_code == 200:
       myself = r.json()
  except requests.exceptions.RequestException as e:
    print 'get_user_info_from qq failed: %s' % e

  return myself

#获取好友列表
def get_friend_info():
  _url = urlparse.urljoin(openqq_url,'/openqq/get_friend_info')
  _header = {'Content-Type':'application/json','Connection':'close'}

  friendlist = []
  try:
     r = requests.get(_url ,headers = _header)
     if r.status_code == 200:
       friendlist  = r.json()
  except requests.exceptions.RequestException as e:
    print 'get_frind_info_from qq failed: %s' % e

  return friendlist


#获取群列表(不包含群成员)
def get_group_basic_info():
  _url = urlparse.urljoin(openqq_url,'/openqq/get_group_basic_info')
  _header = {'Content-Type':'application/json','Connection':'close'}

  grouplist = []
  try:
     r = requests.get(_url ,headers = _header)
     if r.status_code == 200:
       grouplist  = r.json()
  except requests.exceptions.RequestException as e:
    print 'get_group_basic_info_from qq failed: %s' % e

  return grouplist

#获取讨论组列表
def get_discuss_info():
  _url = urlparse.urljoin(openqq_url,'/openqq/get_discuss_info')
  _header = {'Content-Type':'application/json','Connection':'close'}

  discusslist = []
  try:
     r = requests.get(_url ,headers = _header)
     if r.status_code == 200:
       discusslist = r.json()
  except requests.exceptions.RequestException as e:
    print 'get_discuss_info_from_qq failed: %s' % e

  return discusslist 

#获取 qq 好友、群、讨论组列表中每一个的 name 与 id 对应关系，因为mojo-webqq 每次扫描登录会导致 id 变化，故获取 name 与 id 的映射关系
def get_name_id_map(myself = {},friendlist = [],grouplist = [],discusslist = []):
  global NameId
  
  if myself:
    _id   = myself.get('id')
    NameId['Myself'] = _id

  for f in xrange(len(QqFriend)):
    friend = QqFriend[f]
    if not friend:
      continue
    _name = friend.get('name')
    _id   = friend.get('id')
    NameId[_name] = _id

  for g in xrange(len(QqGroup)):
    group = QqGroup[g]
    if not group:
      continue
    _name = group.get('name')
    _id   = group.get('id')
    NameId[_name] = _id

  for d in xrange(len(QqDiscuss)):
    discuss = QqDiscuss[d]
    if not discuss:
      continue
    _name = discuss.get('name')
    _id   = discuss.get('id')
    NameId[_name] = _id
    

#可能需要定时执行该函数，以保证获取最新最准确的 name 与 id 的映射关系
def qq_init():
  myself = get_user_info()
  friendlist = get_friend_info()
  grouplist = get_group_basic_info()
  discusslist = get_discuss_info()
  get_name_id_map(myself,friendlist,grouplist,discusslist)

def urlencode(s):
  return urllib2.quote(s)

def urldecode(s):
  #return urllib2.unquote(s).decode('utf8')
  return urllib2.unquote(s)

#发送好友消息
def send_qq_message(upid = -1,content = ''):
  name = MyidName.get(upid)
  _id = NameId.get(name)
  response = {'info':'','status':'error'}
  if not _id:  #没有在 mojo-webqq 中找到好友
    response['info'] = "check your upid,please make sure it's right"
    return response 

  _url = ''
  if upid / 100 == 1:  #报警信息发送对象为好友
    _url = urlparse.urljoin(openqq_url,'/openqq/send_friend_message')
  elif upid / 200 == 1:  #报警信息发送对象为群
    _url = urlparse.urljoin(openqq_url,'/openqq/send_group_message')
  elif upid / 300 == 1: #报警信息发送对象为讨论组
    _url = urlparse.urljoin(openqq_url,'/openqq/send_discuss_message')
  else:
    response['info'] = "your upid is not enabled"
    return response 


  _headers = {'Connection':'close','Content-Type':'application/x-www-form-urlencoded'}
  _params = {'id':_id,'content':content}
  _data = urlencode(_params)

  try:
    s = requests.session()
    s.keep_alive = False
    a = requests.adapters.HTTPAdapter(max_retries= 2)
    s.mount(openqq_url,a)
    r = s.post(_url,verify = False,headers = _headers,timeout = 10, data =_data)
    #r = requests.post(_url,data =_params)
    if r.status_code == 200:
      #{"status":"发送成功","id":23910327,"code":0} #code为 0 表示发送成功
      result = r.json()
      code = int(result.get('code'))
      status = result.get('status')
      if code == 0:
        response['status'] = 'ok'
        response['info'] = 'send successfully'
      else:
        response['info'] = status
  except requests.exceptions.RequestException as e:
    response['info'] = 'send failed: %s' % e

  return response


#接收报警消息，并发送到指定对象
@app.route('/qqapi/upwarning/', methods=['POST'])
@app.route('/qqapi/upwarning', methods=['POST'])
def ReceiveAlarmMsg():
  alarm_msg = {}
  response = {'status':'error','info':''}
  if not request.is_json:
    alarm_msg = json.loads(request.data)
  else:
    alarm_msg = request.get_json()
  if not alarm_msg or not alarm_msg.get('content'):
    response['info'] = 'you give no warning messages'
    return json.dumps(response) 

  upid = int(alarm_msg.get('upid'))
  content = alarm_msg.get('content')

  #报警信息发送到指定对象
  response = send_qq_message(upid,content)
  return json.dumps(response) 


#使用图灵接口智能聊天,图灵接口说明： https://www.kancloud.cn/turing/web_api/522992
def SmartTuling(info = ''):
  #暂时只支持文本类型
  query = {
    "reqType":0,  #默认为文本类型
    "perception": {
        "inputText": {
            "text": info
        },
        "inputImage": {
            "url": ""
        },
        "inputMedia":{
            "url": ""
        },
    },
    "userInfo": {
        "apiKey": "3c75ff63e01b4b328e67f6788a6e4f80",
        "userId": "111412"
    }
  }
  _url = 'http://www.tuling123.com/openapi/api'         #v1
  _url = 'http://openapi.tuling123.com/openapi/api/v2'  #v2
  _header = {'Content-Type':'application/json','Connection':'close'}


  reply = ''
  response = {}
  try:
     r = requests.post(_url ,headers = _header,data = json.dumps(query))
     response = r.json()
     if 'results' in response:  #包含 results 字段的应该是正常返回,此处就不用判断返回状态码的方式作判断了
       results = response.get('results')
       for r in results:
         resultType = r.get('resultType')
         values = r.get('values')
         reply = values.get(resultType) + '\n'
  except requests.exceptions.RequestException as e:
    print 'get answer from tuling failed: %s' % e
    reply = '我没明白你的意思，重新换种方式跟我说吧！'

  return reply





#mojo-webqq 会对于指定事件进行上报,该接口做一些处理
@app.route('/qqapi/anypost/', methods=['POST'])
@app.route('/qqapi/anypost', methods=['POST'])
def QqAnyPost():
  qqpost = {}
  if not request.is_json:
    qqpost = json.loads(request.data)
  else:
    qqpost = request.get_json()
  post_type = qqpost.get('post_type')

  response = {
    "reply":"",    #要回复消息，必须包含reply的属性
    #"shutup": 1,        #可选，是否对消息发送者禁言
    #"shutup_time": 60,  #可选，禁言时长，默认60s
  }
  if post_type == 'receive_message':
    msg_type = qqpost.get('type')
    content = qqpost.get('content')
    if msg_type == 'friend_message':
      response['reply'] = SmartTuling(content)  #接收到好友消息，调用图灵接口智能回复
      return json.dumps(response)
    elif msg_type == 'group_message':
      None
    elif msg_type == 'discuss_message':
      None

  elif post_type == 'send_message':
    content = qqpost.get('content')
    print 'send_message: %s' % content #发送消息事件上报后不做其他处理，可以简单记录日志

  elif post_type == 'event':
    event = qqpost.get('event')
    if event == 'login':
      print 'mojo-webqq login'
    elif event == 'stop':
      print 'mojo-webqq stop'

  else:
    None

  return ''
